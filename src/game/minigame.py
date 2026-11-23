from abc import ABC, abstractmethod
from typing import Any


class MiniGame(ABC):
    """Abstract class representing a mini-game"""

    def __init__(self, name: str, description: str, is_active: bool = True,) -> None:
        """Initializes mini-game information

        Args:
            name: displayed mini-game name
            description: Short mini-game's rules explanation
            is_active: Indicates whether the game is active
        """
        self.name = name
        self.description = description
        self.is_active = is_active

    @abstractmethod
    def start_game(self, players_discord_ids: list[str]) -> None:
        """Starts the mini-game for all the players in the list

        Args:
            players_discord_ids: players' discord ids
        """
        pass

    @abstractmethod
    def analyze_results(self, match_data: dict[str, Any]) -> None:
        """Analyzes the results of the game and updates game state

        Args:
            match_data: Data from the game's match
        """
        pass

    @abstractmethod
    def calculate_points(self) -> dict[str, int]:
        """Calculates the points of all the players in the game

        Returns:
            Dictionary mapping each player's Discord ID to their score
        """
        pass

