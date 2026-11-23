from dataclasses import dataclass


@dataclass
class Player:
    discord_id : str
    riot_puuid : str
    riot_game_name : str
    riot_tag_line : str
    global_score : int = 0

    def add_points(self, points : int) -> None:
        self.global_score += points
