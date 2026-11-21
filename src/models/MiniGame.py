from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, Any
from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.Party import Party


class MiniGame(Base):
    __tablename__ = "mini_games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    party_id: Mapped[str] = mapped_column(ForeignKey("parties.id", ondelete="CASCADE"), nullable=False)
    game_type: Mapped[str] = mapped_column(String(32), nullable=False)

    target_participant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_champion_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    player_grids: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)

    party: Mapped[Party] = relationship("Party", back_populates="games")

    __mapper_args__ = {
        "polymorphic_on": "game_type",
        "polymorphic_identity": "MINI_GAME",
    }
