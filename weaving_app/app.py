import logging
import queue

from weaving_app.services import PicturesBatchService, SurfaceMovementService

logger = logging.getLogger()


def main() -> None:
    q = queue.Queue()
    services = SurfaceMovementService(q), PicturesBatchService(q)
    for service in services:
        service.daemon = True
        service.start()
        service.join()


if __name__ == "__main__":
    main()
