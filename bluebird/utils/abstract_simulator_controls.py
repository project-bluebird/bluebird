"""
Contains the AbstractSimulatorControls class
"""

from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Union

from bluebird.utils.properties import Scenario
from bluebird.utils.properties import SimProperties


class AbstractSimulatorControls(ABC):
    """Abstract class defining simulator control functions"""

    @property
    @abstractmethod
    def properties(self) -> Union[SimProperties, str]:
        """
        Returns the simulator's current properties, or a string to indicate an error
        """

    @abstractmethod
    def load_scenario_(self, scenario: Scenario) -> Optional[str]:
        """
        Load the specified scenario. Returns None if the scenario was loaded, or a str
        with an error description
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

    @abstractmethod
    def step(self) -> Optional[str]:
        """
        Step the simulation forward one increment when in agent mode (specified by the
        speed property)
        :returns None: If simulation was stepped
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
