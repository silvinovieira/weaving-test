"""
VelocitySensorController is a fake controller to give linear velocity of fabric using a cool Perlin Noise.
"""

from .generators import VelocityGenerator


class VelocitySensorController:
    """
    VelocitySensorController simulates a fabric velocity sensor using Perlin noise.
    This class provides methods to start and stop the velocity sensor, as well as to obtain the current fabric velocity.

    Attributes
    ----------
    _velocity_generator : VelocityGenerator
        Instance of the velocity generator.

    Methods
    -------
    start_sensor()
        Start the fabric velocity sensor.
    stop_sensor()
        Stop the fabric velocity sensor.
    get_velocity() -> float
        Get the current fabric velocity.
    """

    def __init__(self) -> None:
        self._velocity_generator = VelocityGenerator()

    def start_sensor(self) -> None:
        """
        Start the fabric velocity sensor.

        Returns
        -------
        None
        """

        self._velocity_generator.start_generator()

    def stop_sensor(self) -> None:
        """
        Stop the fabric velocity sensor.

        Returns
        -------
        None
        """

        self._velocity_generator.stop_generator()

    def get_velocity(self) -> float:
        """
        Get the current fabric velocity.

        Returns
        -------
        float
            The current fabric velocity.
        """

        return self._velocity_generator.get_velocity()
