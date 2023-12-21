from hardware_controllers.velocity_sensor_controller import VelocitySensorController


def measure_velocity(controller: VelocitySensorController) -> float:
    """Returns the velocity in centimeters per minute (cm/min)"""
    controller.start_sensor()
    velocity = controller.get_velocity()
    controller.stop_sensor()
    return velocity


def measure_displacement(velocity: float, time: float) -> float:
    """
    Args:
        velocity (float): The velocity in cm/min.
        time (float): The time in minutes.

    Returns:
        float: The displacement in centimeters (cm).
    """
    displacement = velocity * time
    return displacement
