import numpy as np

from hardware_controllers.cameras_controller import LightType
from weaving_app.pictures_batch import take_pictures
from weaving_app.surface_movement import measure_velocity


def test_measure_velocity(mocker):
    mock_controller = mocker.Mock()
    mock_controller.get_velocity.return_value = 5.0

    result = measure_velocity(mock_controller)

    assert result == 5.0
    mock_controller.start_sensor.assert_called_once_with()
    mock_controller.get_velocity.assert_called_once_with()
    mock_controller.stop_sensor.assert_called_once_with()


def test_take_pictures(mocker):
    mock_controller = mocker.Mock()
    mock_tuple = (np.array([1, 2]), 3.0, 4.0, 5, np.array([6, 7]), 8.0, 9.0, 10)
    mock_controller.collect_pictures.return_value = mock_tuple

    pictures = take_pictures(mock_controller)

    mock_controller.open_cameras.assert_called_once()
    assert mock_controller.set_light_type.call_count == 2
    assert mock_controller.trigger.call_count == 2
    assert mock_controller.collect_pictures.call_count == 2
    assert isinstance(pictures, dict)
    assert set(pictures.keys()) == {LightType.GREEN, LightType.BLUE}
    assert all(pictures[lt] == mock_tuple for lt in pictures.keys())
