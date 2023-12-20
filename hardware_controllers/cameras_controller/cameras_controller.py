"""
CamerasController is a fake controller to take pictures of fabric (or maybe some cute pets).
"""

import numpy as np
from PIL import Image
from time import sleep
from random import choice, uniform as random_uniform
from typing import List, Tuple, Optional
from pathlib import Path
from threading import Event, Lock

from . import LightType, CameraPosition
from .errors import PicturesNotAvailableError, PictureNotFoundError, CamerasNotReadyError, LightTypeNotDefinedError, \
    TriggerFailedError

ONE_SECOND = 1
ONE_MILLISECOND = ONE_SECOND * 0.001


class CamerasController:
    """
    CamerasController simulates a camera set of cameras sensors using pets pictures.

    This class provides methods to trigger the cameras to capture the pictures, as well to collect them.

    Attributes
    ----------
    _cameras_ready : bool
        Flag to indicate whether cameras are ready or not.
    _cameras_ready_lock : Lock
        Cameras ready flag lock to guarantee that the flag read/write operations are thread safe.
    _global_trigger_lock : Lock
        Trigger lock to guarantee that the trigger action is thread safe.
    _light_type : LightType, optional
        Currently set light type to capture pictures.
    _light_type_lock : Lock
        Light type lock to guarantee that the light type read/write operations are thread safe.
    _green_pictures_available : Event
        Pictures available flag to indicate whether green pictures are available or not.
    _blue_pictures_available : Event
        Pictures available flag to indicate whether blue pictures are available or not.
    _DIAPHRAGM_OPENINGS : List[float]
        Possible diaphragm opening of these cameras' sensors.
    _ISOS : List[int]
        Possible ISO values of these cameras' sensors.
    _EXPOSITION_TIME_LOWER_LIMIT : float
        Minimum exposure time of these cameras' sensors.
    _EXPOSITION_TIME_UPPER_LIMIT : float
        Maximum exposure time of these cameras' sensors.
    _COLLECTING_PICTURES_BASE_SLEEP_TIME : int
        Base sleep time to sleep during pictures collecting to simulate bus communication delay.
    _OPEN_CAMERAS_BASE_SLEEP_TIME : int
        Base sleep time to sleep during cameras initialization to simulate cameras firmware startup.

    Methods
    -------
    open_cameras()
        Prepares de cameras to be ready to use.
    set_light_type()
        Sets the light type to be enabled in the next captures.
    trigger()
        Trigger the cameras shutter to capture the pictures.
    collect_pictures()
        Collects the pictures that were taken previously from all cameras with the `trigger()` method.
    _calculate_open_sleep_time()
        Calculate a cameras opening sleep time to add some uncertainty to it.
    _raise_on_cameras_not_ready()
        Method that raises CamerasNotReadyError exception when cameras are not ready.
    _get_pictures_available_event_by_current_light_type()
        Gets the pictures available event by the current light type.
    _calculate_pictures_collecting_sleep_time()
        Calculate a capturing sleep time to add some uncertainty to capture the pictures.
    _get_pictures()
        Gets the dataclass with the wanted pictures.
    _get_picture()
        Gets the dataclass with the wanted picture - only one camera.
    _create_picture_filepath()
        Creates the picture filepath using the light type and camera position information's.
    """

    _DIAPHRAGM_OPENINGS: List[float] = [2.8, 5, 5.6, 8, 11]
    _ISOS: List[int] = [50, 100, 200, 400, 800, 1600]
    _EXPOSITION_TIME_LOWER_LIMIT: float = 0.00125 * ONE_SECOND
    _EXPOSITION_TIME_UPPER_LIMIT: float = 2 * ONE_SECOND
    _COLLECTING_PICTURES_BASE_SLEEP_TIME: int = 4 * ONE_SECOND
    _OPEN_CAMERAS_BASE_SLEEP_TIME: int = 1 * ONE_SECOND

    def __init__(self) -> None:
        self._cameras_ready = False
        self._cameras_ready_lock = Lock()
        self._global_trigger_lock = Lock()
        self._light_type: Optional[LightType] = None
        self._light_type_lock = Lock()
        self._green_pictures_available = Event()
        self._blue_pictures_available = Event()

    def open_cameras(self) -> None:
        """
        Prepares de cameras to be ready to use.

        Returns
        -------
        None
        """

        with self._cameras_ready_lock:
            sleep(self._calculate_open_sleep_time())
            self._cameras_ready = True

    @staticmethod
    def _calculate_open_sleep_time() -> float:
        """
        Calculate a cameras opening sleep time to add some uncertainty to it.

        Returns
        -------
        float
            Time to open the cameras.
        """

        dispersion_factor = 500 * ONE_MILLISECOND
        sleep_uncertainty = random_uniform(-1, 1) * dispersion_factor
        effective_sleep_time = CamerasController._OPEN_CAMERAS_BASE_SLEEP_TIME + sleep_uncertainty

        return effective_sleep_time

    def _raise_on_cameras_not_ready(self) -> None:
        """
        Method that raises CamerasNotReadyError exception when cameras are not ready.

        Raises
        ------
        CamerasNotReadyError
            When cameras are not ready to be used.

        Returns
        -------
        None
        """

        with self._cameras_ready_lock:
            if not self._cameras_ready:
                raise CamerasNotReadyError('Cannot trigger cameras that are not ready to be used')

    def _get_pictures_available_event_by_current_light_type(self) -> Event:
        """
        Gets the pictures available event by the current light type.

        Raises
        ------
        LightTypeNotDefinedError
            When the light type is not defined.

        Returns
        -------
        Event
            Event of the pictures available event by current light type.
        """

        return self._get_pictures_available_event_by_light_type(self._light_type)

    def _get_pictures_available_event_by_light_type(self, light_type: LightType) -> Event:
        """
        Gets the pictures available event by the light type.

        Raises
        ------
        LightTypeNotDefinedError
            When the light type is not defined.

        Returns
        -------
        Event
            Event of the pictures available event by light type.
        """

        if light_type == LightType.GREEN:
            return self._green_pictures_available
        elif light_type == LightType.BLUE:
            return self._blue_pictures_available
        else:
            raise LightTypeNotDefinedError('The light type was not defined!')

    def set_light_type(self, light_type: LightType) -> None:
        """
        Sets the light type to be enabled in the next captures.

        Parameters
        ----------
        light_type : LightType
            The light type that the client want to use.

        Raises
        ------
        CamerasNotReadyError
            When cameras are not ready to be used.

        Returns
        -------
        None
        """

        self._raise_on_cameras_not_ready()

        with self._light_type_lock:
            self._light_type = light_type

    def trigger(self) -> None:
        """
        Trigger the cameras shutter to capture the pictures.

        Notes
        -----
        The trigger is a consumable, which means that to perform a second trigger, the pictures of that currently
        defined light type need to be collected.

        Raises
        ------
        CamerasNotReadyError
            When cameras are not ready to be used.
        LightTypeNotDefinedError
            When the light type is not defined.
        TriggerFailedError
            When the trigger could not be performed.

        Returns
        -------
        None
        """

        self._raise_on_cameras_not_ready()

        with self._global_trigger_lock:
            with self._light_type_lock:
                pictures_available = self._get_pictures_available_event_by_current_light_type()

                if pictures_available.is_set():
                    raise TriggerFailedError(f'Trigger failed, the previous pictures of the light type '
                                             f'{self._light_type.name} were not collected yet.')

                pictures_available.set()

    def collect_pictures(self,
                         light_type: LightType) -> Tuple[np.ndarray, float, float, int, np.ndarray, float, float, int]:
        """
        Collects the pictures that were taken previously from all cameras with the `trigger()` method.

        Parameters
        ----------
        light_type : LightType
            The light type that the client want to collect.

        Notes
        -----
        Output order:
            (left_picture, left_picture_exposition_time, left_picture_diaphragm_opening, left_picture_iso_value,
             right_picture, right_picture_exposition_time, right_picture_diaphragm_opening, right_picture_iso_value)

        Raises
        ------
        CamerasNotReadyError
            When cameras are not ready to be used.
        LightTypeNotDefinedError
            When the light type is not defined.
        PicturesNotAvailableError
            When the pictures are not available.

        Returns
        -------
        Tuple[np.ndarray, float, float, int, np.ndarray, float, float, int]
            Pictures and their metadata.
        """

        self._raise_on_cameras_not_ready()

        pictures = self._get_pictures(light_type)
        sleep(self._calculate_pictures_collecting_sleep_time())

        return pictures

    @staticmethod
    def _calculate_pictures_collecting_sleep_time() -> float:
        """
        Calculate a capturing sleep time to add some uncertainty to capture the pictures.

        Returns
        -------
        float
            Time to capture a picture.
        """

        dispersion_factor = 1
        sleep_uncertainty = random_uniform(-1, 1) * dispersion_factor
        effective_sleep_time = CamerasController._COLLECTING_PICTURES_BASE_SLEEP_TIME + sleep_uncertainty

        return effective_sleep_time

    def _get_pictures(self,
                      light_type: LightType) -> Tuple[np.ndarray, float, float, int, np.ndarray, float, float, int]:
        """
        Gets the dataclass with the wanted pictures.

        Parameters
        ----------
        light_type : LightType
            The light type that the client want to use.

        Raises
        ------
        LightTypeNotDefinedError
            When the light type is not defined.
        PicturesNotAvailableError
            When the pictures are not available.

        Returns
        -------
        Tuple[np.ndarray, float, float, int, np.ndarray, float, float, int]
            Pictures and their metadata.
        """

        with self._light_type_lock:
            pictures_available = self._get_pictures_available_event_by_light_type(light_type)

            if not pictures_available.is_set():
                raise PicturesNotAvailableError(f'The shutter was not triggered for the light type: {light_type.name}! '
                                                f'Correspondent pictures are not available.')

            left_picture = self._get_picture(light_type, CameraPosition.LEFT)
            right_picture = self._get_picture(light_type, CameraPosition.RIGHT)
            pictures = left_picture + right_picture

            pictures_available.clear()

            return pictures

    def _get_picture(self, light_type: LightType,
                     camera_position: CameraPosition) -> Tuple[np.ndarray, float, float, int]:
        """
        Gets the dataclass with the wanted picture - only one camera.

        Parameters
        ----------
        light_type : LightType
            The light type that the client want to use.
        camera_position : CameraPosition
            The selected camera position of this picture.

        Raises
        ------
        PictureNotFoundError
            When the picture was not found in the expected directory.

        Returns
        -------
        Tuple[np.ndarray, float, float, int]
            Pictures and its metadata.
        """

        filepath = self._create_picture_filepath(light_type, camera_position)
        iso_value = choice(CamerasController._ISOS)
        diaphragm_opening = choice(CamerasController._DIAPHRAGM_OPENINGS)
        exposition_time = random_uniform(CamerasController._EXPOSITION_TIME_LOWER_LIMIT,
                                         CamerasController._EXPOSITION_TIME_UPPER_LIMIT)
        exposition_time = round(exposition_time, 2)
        decoded_picture = np.array(Image.open(filepath))

        return decoded_picture, exposition_time, diaphragm_opening, iso_value

    @staticmethod
    def _create_picture_filepath(light_type: LightType, camera_position: CameraPosition) -> Path:
        """
        Creates the picture filepath using the light type and camera position information's.

        Parameters
        ----------
        light_type : LightType
            The light type that the client want to use.
        camera_position : CameraPosition
            The selected camera position of this picture.

        Raises
        ------
        PictureNotFoundError
            When the picture was not found in the expected directory.

        Returns
        -------
        Path
            The filepath of the selected picture.
        """

        filename = f'{camera_position.value}_picture_{light_type.value}.jpg'
        filepath = Path(__file__).parent.resolve().joinpath('pictures').joinpath(filename)

        if not filepath.is_file():
            raise PictureNotFoundError(f'The picture was not found with the expected filepath {filepath}')

        return filepath
