import asyncio
import logging
import queue
import threading
import time

import aiohttp
import numpy as np
import pandas as pd

from weaving_app.services.velocity import VelocitySensorService


class SurfaceMovementService(threading.Thread):
    SURFACE_MOVEMENT_URL = "http://127.0.0.1:5000/surface_movement"
    SERVER_REQUEST_PERIOD = 2  # seconds
    CAMERA_VERTICAL_FIELD_OF_VIEW = 25  # cm
    DISPLACEMENT_THRESHOLD = CAMERA_VERTICAL_FIELD_OF_VIEW * 0.9  # cm
    MOVING_AVERAGE_FILTER_WINDOW_SIZE = 3

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
            velocities, samples = self.get_clean_velocity_data()
            velocity = self.measure_velocity(velocities)
            displacement = self.measure_displacement(velocity, samples)

            surface_data = {"velocity": velocity, "displacement": displacement}
            self.logger.info(surface_data)

            self.displacement_to_threshold -= displacement

            if self.displacement_to_threshold <= 0:
                self.logger.info("Threshold displacement reached")
                self.surface_queue.put(surface_data)
                self.displacement_to_threshold += self.DISPLACEMENT_THRESHOLD

            asyncio.run(self.post_surface_data(surface_data))

            time.sleep(self.SERVER_REQUEST_PERIOD)

    def get_clean_velocity_data(self) -> tuple[list, int]:
        """Removes outliers and apply moving average filter"""
        samples = self.velocity_queue.qsize()
        if not samples:
            return [], 0
        raw_velocities = [self.velocity_queue.get() for _ in range(samples)]
        filtered_velocities = self.__filter_outliers_iqr(raw_velocities)
        velocities = self.__filter_moving_average(filtered_velocities)
        return velocities, samples

    @staticmethod
    def measure_velocity(velocities: list) -> float:
        """Returns the average velocity in cm/min"""
        if not velocities:
            return 0.0
        return np.mean(velocities)

    @staticmethod
    def measure_displacement(velocity: float, samples: int) -> float:
        """Returns the displacement in cm"""
        time_ = samples / VelocitySensorService.SAMPLE_RATE / 60  # min
        return velocity * time_

    @staticmethod
    def __filter_outliers_iqr(data: list) -> list:
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        filtered_data = [value for value in data if lower_bound < value < upper_bound]
        return filtered_data

    @staticmethod
    def __filter_moving_average(data: list) -> list:
        data_series = pd.Series(data)
        window_size = SurfaceMovementService.MOVING_AVERAGE_FILTER_WINDOW_SIZE
        moving_average = data_series.rolling(window=window_size).mean()
        return moving_average[window_size:].tolist()

    async def post_surface_data(self, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.SURFACE_MOVEMENT_URL, data=data) as response:
                self.logger.info(f"Surface response status code: {response.status}")
