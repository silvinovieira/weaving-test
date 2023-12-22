import asyncio
import logging
import queue
import threading
import time

import aiohttp
import numpy as np

from hardware_controllers.cameras_controller import CamerasController, LightType
from hardware_controllers.velocity_sensor_controller import VelocitySensorController


class VelocitySensorService(threading.Thread):
    SAMPLE_RATE = 50  # Hz

    def __init__(self, velocity_queue: queue.Queue, logger: logging.Logger):
        threading.Thread.__init__(self)
        self.queue = velocity_queue
        self.controller = VelocitySensorController()
        self.logger = logger

    def run(self):
        self.logger.debug("Starting VelocitySensorService")
        while True:
            self.controller.start_sensor()
            velocity = self.controller.get_velocity()
            self.controller.stop_sensor()
            self.logger.debug(f"Velocity: {velocity}")
            self.queue.put(velocity)
            time.sleep(1 / self.SAMPLE_RATE)


class SurfaceMovementService(threading.Thread):
    SURFACE_MOVEMENT_URL = "http://127.0.0.1:5000/surface_movement"
    SERVER_REQUEST_PERIOD = 2  # seconds
    CAMERA_VERTICAL_FIELD_OF_VIEW = 25  # cm
    DISPLACEMENT_THRESHOLD = CAMERA_VERTICAL_FIELD_OF_VIEW * 0.9  # cm

    def __init__(
        self,
        velocity_queue: queue.Queue,
        surface_queue: queue.Queue,
        logger: logging.Logger,
    ):
        threading.Thread.__init__(self)
        self.surface_queue = surface_queue
        self.velocity_queue = velocity_queue
        self.displacement_to_threshold = self.DISPLACEMENT_THRESHOLD
        self.logger = logger

    def run(self):
        self.logger.debug("Starting SurfaceMovementService")
        while True:
            velocity = self.measure_velocity()
            displacement = self.measure_displacement(velocity)

            surface_data = {"velocity": velocity, "displacement": displacement}
            self.logger.info(surface_data)

            self.displacement_to_threshold -= displacement

            if self.displacement_to_threshold <= 0:
                self.logger.info("Threshold displacement reached")
                self.surface_queue.put(surface_data)
                self.displacement_to_threshold += self.DISPLACEMENT_THRESHOLD

            asyncio.run(self.post_surface_data(surface_data))

            time.sleep(self.SERVER_REQUEST_PERIOD)

    def measure_velocity(self) -> float:
        """Returns the velocity in cm/min"""
        samples = self.velocity_queue.qsize()
        if not samples:
            return 0.0
        velocities = [self.velocity_queue.get() for _ in range(samples)]
        return np.mean(velocities)

    def measure_displacement(self, velocity: float) -> float:
        """Returns the displacement in cm"""
        time_ = self.SERVER_REQUEST_PERIOD / 60  # min
        return velocity * time_

    async def post_surface_data(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.SURFACE_MOVEMENT_URL, data=data) as response:
                self.logger.info(f"Surface response status code: {response.status}")


class PicturesBatchService(threading.Thread):
    PICTURES_BATCH_URL = "http://127.0.0.1:5000/pictures_batch"

    def __init__(self, surface_queue: queue.Queue, logger: logging.Logger):
        threading.Thread.__init__(self)
        self.queue = surface_queue
        self.controller = CamerasController()
        self.logger = logger

    def run(self):
        self.logger.debug("Starting PicturesBatchService")
        while True:
            if not self.queue.empty():
                self.logger.debug(f"Queue size: {self.queue.qsize()}")
                self.logger.info("Received surface data on pictures service")
                surface_data = self.queue.get()
                pictures = self.take_pictures()
                self.queue.task_done()
                asyncio.run(self.post_pictures_data(pictures, surface_data))

    def take_pictures(self):
        pictures = {}
        self.controller.open_cameras()
        for light_type in (LightType.BLUE, LightType.GREEN):
            self.logger.info(f"Taking pictures for light type {light_type}")
            self.controller.set_light_type(light_type)
            self.controller.trigger()
        # Separates collect from trigger to minimize displacement between pictures
        for light_type in (LightType.BLUE, LightType.GREEN):
            self.logger.info(f"Collecting pictures for light type {light_type}")
            pictures[light_type] = self.controller.collect_pictures(light_type)
        return pictures

    async def post_pictures_data(self, pictures, surface_data):
        data = {
            "lights": [
                {
                    "light": LightType.BLUE.value,
                    "surface_velocity": surface_data["velocity"],
                    "surface_displacement": surface_data["displacement"],
                },
                {
                    "light": LightType.GREEN.value,
                    "surface_velocity": surface_data["velocity"],
                    "surface_displacement": surface_data["displacement"],
                },
            ]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.PICTURES_BATCH_URL, data=data) as response:
                self.logger.info(f"Pictures response status code: {response.status}")
