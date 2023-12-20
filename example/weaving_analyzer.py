#! /usr/bin/env python3

"""
This is the "golden standard" of this test.
Golden Standard doesn't mean that it is the best implementation!
"""

from PIL import Image

from hardware_controllers.cameras_controller import CamerasController, LightType, CameraPosition


class WeavingAnalyzer:
    def __init__(self) -> None:
        self.cameras_controller = CamerasController()
        print("Weaving Analyzer test initialized.")

    def start(self) -> None:
        print("Starting all the handlers and runners.")
        self.cameras_controller.open_cameras()
        print("All started!")

    def test_cameras(self) -> None:
        self.cameras_controller.set_light_type(LightType.BLUE)
        self.cameras_controller.trigger()
        self.cameras_controller.set_light_type(LightType.GREEN)
        self.cameras_controller.trigger()

        blue_pictures = self.cameras_controller.collect_pictures(LightType.BLUE)
        green_pictures = self.cameras_controller.collect_pictures(LightType.GREEN)

        self.show_pictures_and_metadata(blue_pictures, LightType.BLUE, show=True)
        self.show_pictures_and_metadata(green_pictures, LightType.GREEN, show=True)

    def show_pictures_and_metadata(self, pictures: tuple, light_type: LightType, *, show: bool = False) -> None:
        print(f'\n*** {light_type.name} LIGHT ***')
        left_picture = pictures[:4]
        right_picture = pictures[4:]

        self.show_picture_and_metadata(left_picture, CameraPosition.LEFT, show=show)
        self.show_picture_and_metadata(right_picture, CameraPosition.RIGHT, show=show)

    @staticmethod
    def show_picture_and_metadata(picture: tuple, camera_position: CameraPosition, *, show: bool = False) -> None:
        print(f'{camera_position.value.capitalize()} picture:')
        print(f'· iso: {picture[3]}')
        print(f'· exposure time: {picture[1]} seconds')
        print(f'· diaphragm opening: {picture[2]} f-stops')
        print(f'· picture dimensions: {picture[0].shape[1]} (w) x {picture[0].shape[0]} (h) pixels')
        print(f'· # of color channels: {picture[0].shape[2]}')

        if show:
            picture = Image.fromarray(picture[0])
            picture.show()


def main() -> None:
    weaving_analyzer = WeavingAnalyzer()
    weaving_analyzer.start()
    weaving_analyzer.test_cameras()


if __name__ == '__main__':
    main()
