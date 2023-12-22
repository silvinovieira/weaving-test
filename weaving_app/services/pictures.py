import asyncio
import http
import logging
import queue
import threading

import aiohttp

from hardware_controllers.cameras_controller import CamerasController, LightType


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
                status_code = response.status
                self.logger.info(f"Pictures response status code: {status_code}")
                if status_code != http.HTTPStatus.CREATED.value:
                    self.logger.warning("Unexpected response")
