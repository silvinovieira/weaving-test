import queue

from weaving_app.logger import configure_logger
from weaving_app.services.pictures import PicturesBatchService
from weaving_app.services.surface import SurfaceMovementService
from weaving_app.services.velocity import VelocitySensorService


def main() -> None:
    logger = configure_logger()

    velocity_queue = queue.Queue()
    surface_queue = queue.Queue()

    velocity_service = VelocitySensorService(velocity_queue, logger)
    velocity_service.daemon = True

    surface_service = SurfaceMovementService(velocity_queue, surface_queue, logger)
    surface_service.daemon = True

    pictures_service = PicturesBatchService(surface_queue, logger)
    pictures_service.daemon = True

    velocity_service.start()
    surface_service.start()
    pictures_service.start()

    velocity_service.join()
    surface_service.join()
    pictures_service.join()


if __name__ == "__main__":
    main()
