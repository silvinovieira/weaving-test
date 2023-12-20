"""
Enumerator with the possible light types of this cameras' controller.
"""

from enum import Enum


class LightType(Enum):
    GREEN = 'green_light'
    BLUE = 'blue_light'
