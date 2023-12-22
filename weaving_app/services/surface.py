import asyncio
import logging
import queue
import threading
import time

import aiohttp
import numpy as np


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
