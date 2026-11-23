import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.repositories.user_repo import UserRepository


async def test_user_repository_crud(db_session: AsyncSession):
    repo = UserRepository(db_session)

    user = User(
        discord_id="123",
        riot_puuid="puuid-123",
        riot_game_tag="Faker",
        riot_tag_line="KR",
        global_score=0,
    )
    saved = await repo.save(user)
    await db_session.commit()

    by_discord = await repo.get_by_discord_id("123")
    assert by_discord is not None
    assert by_discord.riot_game_tag == "Faker"

    by_puuid = await repo.get_by_puuid("puuid-123")
    assert by_puuid is not None
    assert by_puuid.discord_id == "123"


async def test_user_repository_score_and_leaderboard(db_session: AsyncSession):
    repo = UserRepository(db_session)

    u1 = User(discord_id="u1", riot_puuid="p1", riot_game_tag="T1", riot_tag_line="KR", global_score=10)
    u2 = User(discord_id="u2", riot_puuid="p2", riot_game_tag="GENG", riot_tag_line="KR", global_score=50)
    u3 = User(discord_id="u3", riot_puuid="p3", riot_game_tag="DK", riot_tag_line="KR", global_score=30)
    db_session.add_all([u1, u2, u3])
    await db_session.commit()

    # Test add score
    updated = await repo.add_score("u1", 100)
    await db_session.commit()
    assert updated is not None
    assert updated.global_score == 110

    # Test leaderboard
    leaderboard = await repo.get_leaderboard(limit=2)
    assert len(leaderboard) == 2
    assert leaderboard[0].discord_id == "u1"  # 110
    assert leaderboard[1].discord_id == "u2"  # 50
