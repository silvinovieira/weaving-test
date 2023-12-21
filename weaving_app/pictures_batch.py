from typing import Dict, Tuple

import numpy as np

from hardware_controllers.cameras_controller import CamerasController, LightType


def take_pictures(
    controller: CamerasController,
) -> Dict[
    LightType, Tuple[np.ndarray, float, float, int, np.ndarray, float, float, int]
]:
    """
    Takes pictures with the provided camera controller and two different light types:
       - Blue
       - Green

    Returns:
        dict: A dictionary where keys are the light types and the values are tuples containing:
            - Pictures and their metadata
    """
    pictures = {}
    controller.open_cameras()
    for light_type in (LightType.BLUE, LightType.GREEN):
        controller.set_light_type(light_type)
        controller.trigger()
    # Separates collect from trigger to minimize displacement between pictures
    for light_type in (LightType.BLUE, LightType.GREEN):
        pictures[light_type] = controller.collect_pictures(light_type)
    return pictures
