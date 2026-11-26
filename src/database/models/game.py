from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import TimestampMixin, Base

if TYPE_CHECKING:
    from src.database.models.user import User
    from src.database.models.mini_game import MiniGame

# Table d'association gérée par SQLAlchemy (correspond à PARTICIPATION du MCD)
game_participants = Table(
    "game_participants",
    Base.metadata,
    Column("game_id", ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
    Column("user_discord_id", ForeignKey("users.discord_id", ondelete="CASCADE"), primary_key=True),
    Column("match_score", Integer, default=0, nullable=False),  # points_totaux_match du MCD
)

# Alias rétrocompatible
party_participants = game_participants


class Game(Base, TimestampMixin):
    __tablename__ = "games"

    # Attributs issus de l'UML (+String idPartie, +StatutPartie statut, +String riotMatchId)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(20), default="EN_ATTENTE", nullable=False)
    riot_match_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # +Joueur createur
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.discord_id", ondelete="CASCADE"), nullable=False)
    creator: Mapped[User] = relationship("User", foreign_keys=[creator_id])

    # +List~Joueur~ participants
    participants: Mapped[list[User]] = relationship(
        "User",
        secondary=game_participants,
        back_populates="games",
    )

    # +List~MiniJeu~ jeux (plusieurs mini-jeux par partie/game)
    mini_games: Mapped[list[MiniGame]] = relationship(
        "MiniGame",
        back_populates="game",
        cascade="all, delete-orphan",
    )

    @property
    def games(self) -> list[MiniGame]:
        return self.mini_games

    @games.setter
    def games(self, value: list[MiniGame]) -> None:
        self.mini_games = value


# Alias rétrocompatible
Party = Game
