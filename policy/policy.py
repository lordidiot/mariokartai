from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from utils import Scancode
from typing import Optional

@dataclass
class State:
    screen: np.ndarray

@dataclass
class Action:
    keys: set[Scancode]

class Policy(ABC):
    """
    Abstract class for policies
    """

    """
    Get the action to take given the current state
    @param state: the current state
    @return: the action to take or None if the policy is done
    """
    @abstractmethod
    def get_action(self, state: State) -> Optional[Action]:
        pass
