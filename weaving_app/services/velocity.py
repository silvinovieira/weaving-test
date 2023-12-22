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
            velocity = self.get_velocity()
            self.queue.put(velocity)
            time.sleep(1 / self.SAMPLE_RATE)

    def get_velocity(self):
        """
        Gets the velocity of the fabric in centimeters per minute.

        Returns
        -------
        float
            Returns the velocity of the fabric in cm/min.
        """
        self.controller.start_sensor()
        velocity = self.controller.get_velocity()
        self.controller.stop_sensor()
        self.logger.debug(f"Velocity: {velocity}")
        return velocity
