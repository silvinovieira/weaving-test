import logging
import time

import requests

from hardware_controllers.velocity_sensor_controller import VelocitySensorController
from weaving_app.surface_movement import measure_displacement, measure_velocity

SERVER_URL = "http://127.0.0.1:5000"
SURFACE_MOVEMENT_URL = SERVER_URL + "/surface_movement"
# Period in seconds
SURFACE_MOVEMENT_REQUEST_PERIOD = 2


logger = logging.getLogger()


def main() -> None:
    while True:
        controller = VelocitySensorController()
        velocity = measure_velocity(controller)
        displacement = measure_displacement(
            velocity=velocity, time=SURFACE_MOVEMENT_REQUEST_PERIOD / 60
        )
        response = requests.post(
            SURFACE_MOVEMENT_URL,
            data={"velocity": velocity, "displacement": displacement},
        )
        logger.info(f"Surface movement response status code: {response.status_code}")
        time.sleep(SURFACE_MOVEMENT_REQUEST_PERIOD)


if __name__ == "__main__":
    main()
