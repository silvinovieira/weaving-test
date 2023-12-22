import logging
import queue
from unittest.mock import patch

from weaving_app.services.surface import SurfaceMovementService
from weaving_app.services.velocity import VelocitySensorService


@patch("weaving_app.services.velocity.VelocitySensorController")
def test_get_velocity(mock_controller):
    mock_controller.return_value.get_velocity.return_value = 42.0

    velocity_queue = queue.Queue()
    logger = logging.getLogger(__name__)

    velocity_service = VelocitySensorService(velocity_queue, logger)
    velocity = velocity_service.get_velocity()

    mock_controller.return_value.start_sensor.assert_called_once()
    mock_controller.return_value.get_velocity.assert_called_once()
    mock_controller.return_value.stop_sensor.assert_called_once()

    assert velocity == 42.0


def test_measure_velocity():
    velocities = [10, 20, 30]
    assert SurfaceMovementService.measure_velocity(velocities) == 20.0


def test_measure_velocity_when_empty():
    assert SurfaceMovementService.measure_velocity([]) == 0.0


def test_measure_velocity_when_negative_value():
    velocities = [-10, 0, 10]
    assert SurfaceMovementService.measure_velocity(velocities) == 0.0


def test_measure_displacement():
    velocity = 50.0
    samples = 100
    expected = velocity * (samples / VelocitySensorService.SAMPLE_RATE / 60)
    assert SurfaceMovementService.measure_displacement(velocity, samples) == expected
