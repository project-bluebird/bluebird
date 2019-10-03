"""
Contains the AbstractSimClient class
"""
# TODO Need to capture common sim states between MachColl / BlueBird and expose here
# TODO Add "using_streams" setting to indicate whether the caches are being
# automatically filled
# TODO Need to pull out logging from the implementations of this

from abc import ABC, abstractmethod
from typing import Iterable, Optional, Union

from semver import VersionInfo

from bluebird.utils.timer import Timer
from bluebird.utils.types import Altitude, Callsign, Heading, LatLon


class AbstractAircraftControls(ABC):
    """
    Abstract class defining aircraft control functions
    """

    @abstractmethod
    def set_cleared_fl(
        self, callsign: Callsign, flight_level: Altitude, **kwargs
    ) -> Optional[str]:
        """
		Set the cleared flight level for the specified aircraft
		:param callsign: The aircraft identifier
		:param flight_level: The flight level to set
		:returns None: If cleared flight level was set
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def add_waypoint_to_route(
        self, callsign: Callsign, target: Union[str, LatLon], **kwargs
    ) -> Optional[str]:
        """
		Append a waypoint to an aircraft's route
		:param callsign:
		:param target: Can either specify an existing waypoint by name, or a LatLon
        position
		:return:
		"""

    # TODO Supported aircraft types
    @abstractmethod
    def create(
        self,
        callsign: Callsign,
        ac_type: str,
        position: LatLon,
        heading: Heading,
        altitude: Altitude,
        speed: int,
    ) -> Optional[str]:
        """
        Create an aircraft
        :param callsign:
        :param ac_type:
        :param position:
        :param heading:
        :param altitude:
        :param speed:
        :return:
        """

    # TODO Needs to return a standard set of properties (instead of str), including:
    # position, alt, speed, route, heading (track), type
    # NOTE callsign=None should return all aircraft
    @abstractmethod
    def get_properties(self, callsign: Optional[Callsign]) -> str:
        """
        Get all the properties for an aircraft
        :param callsign:
        """


class AbstractSimulatorControls(ABC):
    """
    Abstract class defining simulator control functions
    """

    @property
    @abstractmethod
    def sim_state(self) -> str:
        """
        :return: Returns the simulators current state
        """

    @abstractmethod
    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        """
		Load the specified scenario
		:param scenario_name:
		:param speed: Initial speed
		:param start_paused: If specified, will pause the simulator after loading the
        scenario
		:returns None: If the scenario was loaded
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def start(self) -> Optional[str]:
        """
		Start the simulation
		:returns None: If simulation was started
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def reset(self) -> Optional[str]:
        """
		Stop and reset the simulation
		:returns None: If simulation was reset
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def pause(self) -> Optional[str]:
        """
		Pause the simulation
		:returns None: If simulation was paused
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def resume(self) -> Optional[str]:
        """
		Resume the simulation
		:returns None: If simulation was resumed
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def step(self) -> Optional[str]:
        """
		Step the simulation forward one increment (specified by the step_size)
		:returns None: If simulation was stepped
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def get_speed(self) -> float:
        """
		Get the simulator speed (DTMULT for BlueSky)
		:returns None: If speed set
		:returns str: Representing any errors
		:return:
		"""

    @abstractmethod
    def set_speed(self, speed) -> Optional[str]:
        """
		Set the simulator speed (DTMULT for BlueSky)
		:param speed:
		:returns None: If speed set
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        """
		Upload a new scenario to the simulation server
		:param scn_name:
		:param content:
		:returns None: If the scenario was uploaded
		:returns str: To indicate an error
		:return:
		"""

    @abstractmethod
    def get_seed(self) -> int:
        """
		Get the simulator's random seed
		:return:
		"""

    # TODO Add info on supported ranges for seed (may differ between sim
    # implementations, but needs to be fixed for the external API)
    @abstractmethod
    def set_seed(self, seed: int) -> Optional[str]:
        """
		Set the simulator's random seed
		:param seed:
		:return:
		"""

    # TODO Specify the return format so the API doesn't have to do any conversion
    # (instead of str)
    @abstractmethod
    def get_time(self) -> Optional[str]:
        """
		Returns the current simulator time in UTC
		:return:
		"""


class AbstractWaypointControls(ABC):
    """
    Abstract class defining waypoint control functions
    """

    @abstractmethod
    def define(self, name: str, position: LatLon, **kwargs) -> Optional[str]:
        """
        Define a waypoint
        :param name:
        :param position:
        :return:
        """


class AbstractSimClient(ABC):
    """
    Adapter class to provide a common interface between BlueBird and the different
    simulator clients
    """

    @property
    @abstractmethod
    def sim_version(self) -> VersionInfo:
        """
        Return the version of the connected simulation server
        :return:
        """

    @property
    @abstractmethod
    def simulator(self) -> AbstractSimulatorControls:
        """
        :return: Returns the client's simulator controller instance
        :rtype: AbstractSimulatorControls
        """

    @property
    @abstractmethod
    def aircraft(self) -> AbstractAircraftControls:
        """
        :return: Returns the client's aircraft controller instance
        :rtype: AbstractAircraftControls
        """

    @property
    @abstractmethod
    def waypoints(self) -> AbstractWaypointControls:
        """
        :return: Returns the client's waypoint controller instance
        :rtype: AbstractWaypointControls
        """

    @abstractmethod
    def __init__(self, sim_state, ac_data):
        pass

    @abstractmethod
    def start_timers(self) -> Iterable[Timer]:
        """
        Start any timed functions, and return all the Timer instances
        :return:
        """

    @abstractmethod
    def connect(self, timeout=1) -> None:
        """
        Connect to the simulation server
        :param timeout:
        :raises TimeoutException: If the connection could not be made before the timeout
        :return:
        """

    @abstractmethod
    def stop(self, shutdown_sim: bool) -> Optional[bool]:
        """
        Disconnect from the simulation server, and stop the client (including any
        timers)
        :param shutdown_sim: If true, also informs the simulation server to exit
        :return:
        """
