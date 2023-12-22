from weaving_app.surface_movement import measure_velocity


def test_measure_velocity(mocker):
    mock_controller = mocker.Mock()
    mock_controller.get_velocity.return_value = 5.0

    result = measure_velocity(mock_controller)

    assert result == 5.0
    mock_controller.start_sensor.assert_called_once_with()
    mock_controller.get_velocity.assert_called_once_with()
    mock_controller.stop_sensor.assert_called_once_with()
