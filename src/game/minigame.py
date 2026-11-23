from abc import ABC, abstractmethod
from typing import Any


class MiniGame(ABC):
    """Abstract class representing a mini-game"""

    def __init__(self,name: str,description: str,is_active: bool = True,) -> None:
        """Initializes mini-game information

        Args:
            name: displayed mini-game name
            description: Short mini-game's rules explanation
            is_active: Indicates whether the game is active
        """
        self.name = name
        self.description = description
        self.is_active = is_active

