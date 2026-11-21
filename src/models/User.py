from typing import TYPE_CHECKING
from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database.base import Base

if TYPE_CHECKING:
    from src.models.Party import Party


class User(Base):
    __tablename__ = "users"

    discord_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    riot_puuid: Mapped[str] = mapped_column(String(78), unique=True, index=True, nullable=False)
    riot_game_tag: Mapped[str] = mapped_column(String(64), nullable=False)
    riot_tag_line: Mapped[str] = mapped_column(String(16), nullable=False)
    global_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parties: Mapped[list[Party]] = relationship(
        "Party",
        secondary="party_participants",
        back_populates="participants",
    )
