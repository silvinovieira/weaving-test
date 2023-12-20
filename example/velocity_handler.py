from time import sleep
from threading import Thread

from hardware_controllers.velocity_sensor_controller import VelocitySensorController

ONE_HERTZ = 1


class VelocityHandler:
    SAMPLING_RATE = 50 * ONE_HERTZ

    def __init__(self) -> None:
        self._do_run = False
        self.velocity_sensor_controller = VelocitySensorController()
        self.sampler_thread = Thread(target=self.sampler, name='velocity_sampler_thread')

    def start(self) -> None:
        self._do_run = True
        self.velocity_sensor_controller.start_sensor()
        self.sampler_thread.start()

    def stop(self) -> None:
        self._do_run = False
        self.velocity_sensor_controller.stop_sensor()

    def sampler(self):
        while self._do_run:
            sample = self.velocity_sensor_controller.get_velocity()
            sleep(1 / VelocityHandler.SAMPLING_RATE)
