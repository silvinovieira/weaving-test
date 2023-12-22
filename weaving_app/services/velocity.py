import logging
import queue
import threading
import time

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
