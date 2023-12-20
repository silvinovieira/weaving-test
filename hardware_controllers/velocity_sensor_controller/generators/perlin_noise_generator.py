"""
PerlinNoiseGenerator is a generator of Perlin noise, which permits an appearance of realism to a wave.
"""

from random import randint
import noise


class PerlinNoiseGenerator:
    """
    PerlinNoiseGenerator is a generator for Perlin noise values.

    Parameters
    ----------
    t_increment : float, default=0.1
        Increment value for generating noise over time, by default 0.1.

    Attributes
    ----------
    _t_increment : float
        Increment value for generating noise over time.
    _t_value : int
        Current time value used for generating noise.

    Methods
    -------
    new_value()
        Generates a new Perlin noise value.
    """

    def __init__(self, t_increment: float = 0.1) -> None:
        self._t_increment = t_increment
        self._t_value = randint(0, 1000)

    def new_value(self) -> float:
        """
        Generates a new Perlin noise value.

        Returns
        -------
        float
            A new Perlin noise value.
        """

        self._t_value += self._t_increment

        return noise.pnoise1(self._t_value)
