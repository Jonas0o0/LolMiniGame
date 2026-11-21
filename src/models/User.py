from sqlalchemy import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from src.database import Base

class User(Base):
    __tablename__ = "users"

    discord_id: Mapped[str] = mapped_column(String, primary_key=True)
    riot_puuid: Mapped[str] = mapped_column(String, nullable=False)
    riot_game_tag: Mapped[str] = mapped_column(String, nullable=False)
    riot_tag_line: Mapped[str] = mapped_column(String, nullable=False)
    global_score: Mapped[int] = mapped_column(Integer, nullable=False)