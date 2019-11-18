"""
Contains the AbstractSimulatorControls class
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, Iterable

from bluebird.utils.properties import SimProperties, SimState


class AbstractSimulatorControls(ABC):
    """
    Abstract class defining simulator control functions
    """

    @property
    @abstractmethod
    def stream_data(self) -> SimProperties:
        """
        The current stream data of SimProperties. Will be None if streaming is not
        enabled
        """

    @property
    @abstractmethod
    def properties(self) -> Union[SimProperties, str]:
        """
        :return: Returns the simulator's current properties, or a string to indicate an
        error
        """

    # @property
    # def time(self) -> Union[float, str]:
    #     """
    #     :return: Returns the current simulated time, or a string to indicate an
    #     error
    #     """

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
		"""

    @abstractmethod
    def start(self) -> Optional[str]:
        """
		Start the simulation
		:returns None: If simulation was started
		:returns str: To indicate an error
		"""

    @abstractmethod
    def reset(self) -> Optional[str]:
        """
		Stop and reset the simulation
		:returns None: If simulation was reset
		:returns str: To indicate an error
		"""

    @abstractmethod
    def pause(self) -> Optional[str]:
        """
		Pause the simulation
		:returns None: If simulation was paused
		:returns str: To indicate an error
		"""

    @abstractmethod
    def resume(self) -> Optional[str]:
        """
		Resume the simulation
		:returns None: If simulation was resumed
		:returns str: To indicate an error
		"""

    @abstractmethod
    def stop(self) -> Optional[str]:
        """
        Stop the simulation
        :returns None: If simulation was stopped
		:returns str: To indicate an error
        """

    @staticmethod
    @abstractmethod
    def parse_sim_state(val: str) -> Union[SimState, str]:
        """
        Parses a SimState value from the simulator's set of states. Returns a
        string for errors
        """

    @abstractmethod
    def step(self) -> Optional[str]:
        """
		Step the simulation forward one increment (specified by the step_size)
		:returns None: If simulation was stepped
		:returns str: To indicate an error
		"""

    @abstractmethod
    def get_speed(self) -> Union[float, str]:
        """
		Get the simulator speed (DTMULT for BlueSky)
		:returns float: The current sim speed
		:returns str: To indicate an error
		"""

    @abstractmethod
    def set_speed(self, speed: float) -> Optional[str]:
        """
		Set the simulator speed, or the step size if in agent mode (i.e. the meaning of
        this is overloaded and depends on the mode of operation)
		:param speed:
		:returns None: If the speed is set
		:returns str: To indicate an error
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
		"""

    @abstractmethod
    def get_seed(self) -> int:
        """
		Get the simulator's random seed
		"""

    # TODO Add info on supported ranges for seed (may differ between sim
    # implementations, but needs to be fixed for the external API)
    @abstractmethod
    def set_seed(self, seed: int) -> Optional[str]:
        """
        Set the simulator's random seed
        :param seed: The integer seed to set
		:returns None: If the seed was set
		:returns str: To indicate an error
        """
