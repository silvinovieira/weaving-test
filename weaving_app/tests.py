import logging
import queue
from unittest.mock import patch

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
