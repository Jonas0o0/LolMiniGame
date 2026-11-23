import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User, Game, Bingo, GameStatus
from src.repositories.game_repo import GameRepository


@pytest.fixture
async def sample_users(db_session: AsyncSession) -> tuple[User, User, User]:
    u1 = User(
        discord_id="u1",
        riot_puuid="puuid-1",
        riot_game_tag="PlayerOne",
        riot_tag_line="EUW",
        global_score=0,
    )
    u2 = User(
        discord_id="u2",
        riot_puuid="puuid-2",
        riot_game_tag="PlayerTwo",
        riot_tag_line="EUW",
        global_score=10,
    )
    u3 = User(
        discord_id="u3",
        riot_puuid="puuid-3",
        riot_game_tag="PlayerThree",
        riot_tag_line="EUW",
        global_score=20,
    )
    db_session.add_all([u1, u2, u3])
    await db_session.commit()
    return u1, u2, u3


async def test_create_and_get_game(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    bingo = Bingo(game_type="BINGO")
    game = await repo.create(creator=u1, mini_games=[bingo])
    await db_session.commit()

    loaded = await repo.get_by_id(game.id)
    assert loaded is not None
    assert loaded.id == game.id
    assert loaded.creator.discord_id == u1.discord_id
    assert len(loaded.participants) == 1
    assert loaded.participants[0].discord_id == u1.discord_id
    assert len(loaded.mini_games) == 1
    assert loaded.mini_games[0].game_type == "BINGO"


async def test_get_games_by_status(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    g1 = await repo.create(creator=u1, status=GameStatus.EN_ATTENTE)
    g2 = await repo.create(creator=u1, status=GameStatus.EN_COURS)
    await db_session.commit()

    pending = await repo.get_games_by_status(GameStatus.EN_ATTENTE)
    assert len(pending) == 1
    assert pending[0].id == g1.id

    running = await repo.get_games_by_status("EN_COURS")
    assert len(running) == 1
    assert running[0].id == g2.id


async def test_get_active_game_for_user(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, u2, u3 = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1, status=GameStatus.EN_ATTENTE)
    await repo.add_participant(game, u2)
    await db_session.commit()

    active_u1 = await repo.get_active_game_for_user(u1.discord_id)
    assert active_u1 is not None
    assert active_u1.id == game.id

    active_u2 = await repo.get_active_game_for_user(u2.discord_id)
    assert active_u2 is not None
    assert active_u2.id == game.id

    active_u3 = await repo.get_active_game_for_user(u3.discord_id)
    assert active_u3 is None


async def test_add_and_remove_participant(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, u2, _ = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1)
    await db_session.commit()

    # Ajout participant
    updated = await repo.add_participant(game.id, u2)
    assert updated is not None
    assert len(updated.participants) == 2
    await db_session.commit()

    # Tentative doublon
    await repo.add_participant(game.id, u2)
    assert len(game.participants) == 2

    # Retrait participant
    after_remove = await repo.remove_participant(game.id, u2.discord_id)
    assert after_remove is not None
    assert len(after_remove.participants) == 1
    assert after_remove.participants[0].discord_id == u1.discord_id
    await db_session.commit()


async def test_update_status_and_scores(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, u2, _ = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1)
    await repo.add_participant(game, u2)
    await db_session.commit()

    # Changement de statut et riot match id
    updated = await repo.update_status(game.id, GameStatus.TERMINEE, riot_match_id="EUW1_123456789")
    assert updated is not None
    assert updated.status == GameStatus.TERMINEE.value
    assert updated.riot_match_id == "EUW1_123456789"
    await db_session.commit()

    # Mise à jour des scores
    await repo.set_participant_score(game.id, u1.discord_id, 100)
    await repo.set_participant_score(game.id, u2.discord_id, 50)
    await db_session.commit()

    scores = await repo.get_participant_scores(game.id)
    assert scores[u1.discord_id] == 100
    assert scores[u2.discord_id] == 50


async def test_delete_game(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1)
    await db_session.commit()

    deleted = await repo.delete(game.id)
    assert deleted is True
    await db_session.commit()

    not_found = await repo.get_by_id(game.id)
    assert not_found is None
