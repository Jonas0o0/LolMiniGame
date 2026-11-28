from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models.game import Game
    from src.database.models.user import User


class MiniGame(Base):
    """Base class for all mini-games in a game (UML: MiniJeu, MCD: INSTANCE_MINI_JEU)."""
    __tablename__ = "mini_games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    game_type: Mapped[str] = mapped_column(String(32), nullable=False)

    # Vainqueur du mini-jeu (MCD: vainqueur_discord_id)
    winner_discord_id: Mapped[str | None] = mapped_column(ForeignKey("users.discord_id", ondelete="SET NULL"), nullable=True)
    winner: Mapped[User | None] = relationship("User", foreign_keys=[winner_discord_id])

    # Points gagnés par chaque joueur sur ce jeu (MCD: points_jeu dans RESULTAT_JOUEUR)
    # Format: {"discord_id_1": 100, "discord_id_2": 50}
    player_scores: Mapped[dict[str, int] | None] = mapped_column(JSON, nullable=True)

    # Attributs spécifiques à Assassinat
    target_participant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_champion_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Attributs spécifiques au Bingo (stocke les grilles en JSON : donnees_jeu du MCD)
    player_grids: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    # Relation avec la partie / game
    game: Mapped[Game] = relationship("Game", back_populates="mini_games")

    @property
    def party_id(self) -> str:
        return self.game_id

    @party_id.setter
    def party_id(self, value: str) -> None:
        self.game_id = value

    @property
    def party(self) -> Game:
        return self.game

    @party.setter
    def party(self, value: Game) -> None:
        self.game = value

    __mapper_args__ = {
        "polymorphic_on": "game_type",
        "polymorphic_identity": "MINI_GAME",
    }
