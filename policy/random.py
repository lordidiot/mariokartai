import numpy as np
from policy import Policy, State, Action
from utils import Scancode
from typing import Optional

class RandomPolicy(Policy):
    def __init__(self, n_steps: int, keys: list[Scancode], std_dev: float = 1.0):
        self.n_steps = n_steps
        self.keys = keys
        self.n_keys = len(keys)
        self.std_dev = std_dev
        self.t = 0
        self.compute_actions()

    def compute_actions(self):
        white_noise = np.random.normal(0, self.std_dev, (self.n_steps, self.n_keys))
        brown_noise = np.cumsum(white_noise, axis=0)
        min_brown = np.min(brown_noise, axis=0)
        max_brown = np.max(brown_noise, axis=0)
        norm_brown = (brown_noise - min_brown) / (max_brown - min_brown)
        threshold = 0.5
        self.binary_actions = (norm_brown > threshold)

    def get_action(self, _state: State) -> Optional[Action]:
        if self.t >= self.n_steps:
            return None
        binary_actions = self.binary_actions[self.t]
        keys = set(map(lambda x: x[0], filter(lambda x: x[1], zip(self.keys, binary_actions))))
        self.t += 1
        return Action(keys)
