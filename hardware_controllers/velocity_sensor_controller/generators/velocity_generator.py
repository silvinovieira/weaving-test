"""
VelocityGenerator simulates a fabric velocity sensor to be used by the VelocitySensorController.
"""

from time import sleep
from random import random, uniform as random_uniform
from typing import Optional
from threading import Thread

from .perlin_noise_generator import PerlinNoiseGenerator

ONE_HERTZ = 1


class VelocityGenerator:
    """
    VelocityGenerator simulates a fabric velocity sensor using Perlin noise.

    Attributes
    ----------
    _UPDATE_FREQUENCY : int
        Update frequency in Hz.
    _noise_generator : PerlinNoiseGenerator
        Perlin noise generator instance.
    _sleep_time : float
        Time to sleep between updates.
    _current_value : float
        Current fabric velocity value.
    _noisy_value : float
        Fabric velocity value with added noise.
    noise_coefficient : float
        Coefficient to control noise intensity.
    _run_thread : bool
        Flag to control the sensor thread.
    _speed_generator_thread : Thread
        Thread for generating speed values.

    Methods
    -------
    start_sensor()
        Start the fabric velocity sensor.
    get_velocity() -> float
        Get the noisy fabric velocity in cm/min.
    _generate_speed_values()
        Internal method for generating fabric speed values.
    stop_sensor()
        Stop the fabric velocity sensor.
    _ramp(iterations: int, target_value: float, add_noise: bool = True)
        Simulate a ramping velocity change.
    _linear(iterations: int, add_noise: bool = True)
        Simulate a constant velocity period.
    _add_noise()
        Add Perlin noise to the current value.
    """

    _UPDATE_FREQUENCY = 50 * ONE_HERTZ
    _OUTLIER_PROBABILITY = 0.1
    _OUTLIER_AT_ZERO_PROBABILITY = 0.3
    _MINIMUM_VALUE_WITHOUT_NOISE = 0
    _MAXIMUM_VALUE_WITHOUT_NOISE = 100
    _MINIMUM_OUTLIER_VALUE = -150
    _MAXIMUM_OUTLIER_VALUE = 400

    def __init__(self) -> None:
        self._noise_generator = PerlinNoiseGenerator()
        self._sleep_time = 1 / VelocityGenerator._UPDATE_FREQUENCY
        self._current_value = 0
        self._noisy_value = 0
        self.noise_coefficient = 5
        self._run_thread = False
        self._speed_generator_thread: Optional[Thread] = None

    def start_generator(self) -> None:
        """
        Start the fabric velocity sensor.

        Returns
        -------
        None
        """

        if not self._speed_generator_thread or not self._speed_generator_thread.is_alive():
            self._run_thread = True
            self._speed_generator_thread = Thread(target=self._generate_speed_values)
            self._speed_generator_thread.start()

    def stop_generator(self) -> None:
        """
        Stop the fabric velocity sensor.

        Returns
        -------
        None
        """

        self._run_thread = False

    def get_velocity(self) -> float:
        """
        Gets the velocity of the fabric in centimeters per minute.

        Returns
        -------
        float
            Returns the velocity of the fabric in cm/min.
        """

        if self._is_outlier():
            return self._get_outlier_velocity()

        return self._noisy_value

    @staticmethod
    def _is_outlier() -> bool:
        """
        Calculates if the velocity to get will be an outlier or not.

        Returns
        -------
        bool
            True if it will be an outlier, False otherwise.
        """

        if random() < VelocityGenerator._OUTLIER_PROBABILITY:
            return True

        return False

    @staticmethod
    def _get_outlier_velocity() -> float:
        if random() < VelocityGenerator._OUTLIER_AT_ZERO_PROBABILITY:
            return 0

        return random_uniform(VelocityGenerator._MINIMUM_OUTLIER_VALUE, VelocityGenerator._MAXIMUM_OUTLIER_VALUE)

    def _generate_speed_values(self) -> None:
        """
        Internal method for generating fabric speed values.

        Returns
        -------
        None
        """

        while self._run_thread:
            self._ramp(iterations=500, target_value=VelocityGenerator._MAXIMUM_VALUE_WITHOUT_NOISE)
            self._linear(iterations=500)
            self._ramp(iterations=200, target_value=VelocityGenerator._MINIMUM_VALUE_WITHOUT_NOISE)
            self._linear(iterations=200)

    def _ramp(self, iterations: int, target_value: float, add_noise: bool = True) -> None:
        """
        Simulate a ramping velocity change.

        Parameters
        ----------
        iterations : int
            Number of iterations for the ramp.
        target_value : float
            Target value to ramp to.
        add_noise : bool, default=True
            Whether to add noise during the ramp.
        """

        slope = (target_value - self._current_value) / iterations

        for _ in range(iterations):
            self._current_value += slope

            if add_noise:
                self._add_noise()

            sleep(self._sleep_time)

    def _linear(self, iterations: int, add_noise: bool = True) -> None:
        """
        Simulate a constant velocity period.

        Parameters
        ----------
        iterations : int
            Number of iterations for the linear period.
        add_noise : bool, default=True
            Whether to add noise during the linear period.
        """

        for _ in range(iterations):
            if add_noise:
                self._add_noise()

            sleep(self._sleep_time)

    def _add_noise(self) -> None:
        """
        Add Perlin noise to the current value.

        Returns
        -------
        None
        """

        self._noisy_value = self._current_value + self._noise_generator.new_value() * self.noise_coefficient
