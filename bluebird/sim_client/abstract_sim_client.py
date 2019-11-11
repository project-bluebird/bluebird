"""
Contains the AbstractSimClient class
"""

from abc import ABC, abstractmethod
from typing import Iterable, Optional, Union, List, Dict

from semver import VersionInfo

from bluebird.utils.timer import Timer
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties, SimProperties, SimState


class AbstractAircraftControls(ABC):
    """
    Abstract class defining aircraft control functions
    """

    @property
    @abstractmethod
    def stream_data(self) -> List[AircraftProperties]:
        """
        The current stream data of AircraftProperties. May be an empty list if streaming
        is not enabled
        :return:
        """

    @property
    @abstractmethod
    def routes(self) -> Dict[types.Callsign, List]:
        """
        A dict of the current aircraft routes in the scenario, keyed by callsign
        :return:
        """

    @abstractmethod
    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
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
    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        """
        Set the heading of the specified aircraft
        :param callsign:
        :param heading:
        :return:
        """

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        """
        Set the ground speed of the specified aircraft
        :param callsign:
        :param ground_speed:
        :return:
        """

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        """
        Set the vertical speed of the specified aircraft
        :param callsign:
        :param vertical_speed:
        :return:
        """

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        """
        Send the aircraft directly to the specified waypoint
        :param callsign:
        :param waypoint:
        :return:
        """

    @abstractmethod
    def add_waypoint_to_route(
        self, callsign: types.Callsign, waypoint: types.Waypoint, **kwargs
    ) -> Optional[str]:
        """
        Append a waypoint to an aircraft's route
        :param callsign:
        :param target: Can either specify an existing waypoint by name, or a LatLon
        position
        :return:
        """

    # TODO What are the supported aircraft types?
    @abstractmethod
    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
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

    @abstractmethod
    def get_properties(
        self, callsign: types.Callsign
    ) -> Union[AircraftProperties, str]:
        """
        Get all the properties for the specified aircraft
        :param callsign: The aircraft callsign
        :return: String on error
        """

    def get_all_properties(self) -> Dict[types.Callsign, AircraftProperties]:
        """
        Get properties for all aircraft in the scenario
        :return: A dict of all aircraft properties in the simulation
        """


class AbstractSimulatorControls(ABC):
    """
    Abstract class defining simulator control functions
    """

    @property
    @abstractmethod
    def stream_data(self) -> SimProperties:
        """
        The current stream data of SimProperties. May be None if streaming is not
        enabled
        :return:
        """

    @property
    @abstractmethod
    def properties(self) -> Union[SimProperties, str]:
        """
        :return: Returns the simulator's current properties, or a string to indicate an
        error
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
    def stop(self) -> Optional[str]:
        """
        Stop the simulation
        :returns None: If simulation was stopped
		:returns str: To indicate an error
		:return:
        """

    @staticmethod
    @abstractmethod
    def parse_sim_state(val: str) -> Union[SimState, str]:
        """
        Parses a value SimState value from the simulator's set of states. Returns a
        string for errors
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
    def set_speed(self, speed: float) -> Optional[str]:
        """
		Set the simulator speed, or the step size if in agent mode (i.e. the meaning of
        this is overloaded and depends on the mode of operation)
		:param speed:
		:returns None: If the speed is set
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

    @abstractmethod
    def get_time(self) -> float:
        pass

    # TODO Add info on supported ranges for seed (may differ between sim
    # implementations, but needs to be fixed for the external API)
    @abstractmethod
    def set_seed(self, seed: int) -> Optional[str]:
        """
		Set the simulator's random seed
		:param seed:
		:return:
		"""


class AbstractWaypointControls(ABC):
    """
    Abstract class defining waypoint control functions
    """

    # TODO Will need a mapping between each client format and BlueBird's implementation
    @abstractmethod
    def get_all_waypoints(self) -> dict:
        """
        Get all the waypoints (fixes) defined in the simulation
        """

    @abstractmethod
    def define(self, name: str, position: types.LatLon, **kwargs) -> Optional[str]:
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
    def aircraft(self) -> AbstractAircraftControls:
        """
        :return: Returns the client's aircraft controller instance
        :rtype: AbstractAircraftControls
        """

    @property
    @abstractmethod
    def simulation(self) -> AbstractSimulatorControls:
        """
        :return: Returns the client's simulator controller instance
        :rtype: AbstractSimulatorControls
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
    def waypoints(self) -> AbstractWaypointControls:
        """
        :return: Returns the client's waypoint controller instance
        :rtype: AbstractWaypointControls
        """

    @abstractmethod
    def connect(self, timeout: int = 1) -> None:
        """
        Connect to the simulation server
        :param timeout:
        :raises TimeoutException: If the connection could not be made before the timeout
        :return:
        """

    @abstractmethod
    def start_timers(self) -> Iterable[Timer]:
        """
        Start any timed functions, and return all the Timer instances
        :return:
        """

    @abstractmethod
    def stop(self, shutdown_sim: bool = False) -> bool:
        """
        Disconnect from the simulation server, and stop the client (including any
        timers)
        :param shutdown_sim: If true, also informs the simulation server to exit
        :return: If shutdown_sim was requested, the return value will indicate whether
        the simulator was shut down successfully
        """
