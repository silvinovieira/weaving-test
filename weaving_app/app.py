import queue

from weaving_app.logger import configure_logger
from weaving_app.services import PicturesBatchService, SurfaceMovementService


def main() -> None:
    logger = configure_logger()

    q = queue.Queue()

    surface_service = SurfaceMovementService(q, logger)
    surface_service.daemon = True

    pictures_service = PicturesBatchService(q, logger)
    pictures_service.daemon = True

    surface_service.start()
    pictures_service.start()

    surface_service.join()
    pictures_service.join()


if __name__ == "__main__":
    main()
