import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Bingo, Assassination, MiniGame, GameStatus
from src.database.repositories import GameRepository, PartyRepository


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
    assert await repo.set_participant_score(game.id, u1.discord_id, 100) is True
    assert await repo.set_participant_score(game.id, u2.discord_id, 50) is True
    assert await repo.set_participant_score(game.id, "unknown-user", 99) is False
    assert await repo.set_participant_score("unknown-game", u1.discord_id, 99) is False
    await db_session.commit()

    scores = await repo.get_participant_scores(game.id)
    assert scores[u1.discord_id] == 100
    assert scores[u2.discord_id] == 50
    assert await repo.get_participant_scores("unknown-game") == {}


async def test_delete_game(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    bingo = Bingo(game_type="BINGO")
    game = await repo.create(creator=u1, mini_games=[bingo])
    await db_session.commit()

    assert await repo.delete("unknown-game") is False

    deleted = await repo.delete(game.id)
    assert deleted is True
    await db_session.commit()

    assert await repo.get_by_id(game.id) is None
    assert await repo.get_by_id(game.id, load_relations=False) is None
    remaining_mini_games = (await db_session.execute(select(MiniGame))).scalars().all()
    assert remaining_mini_games == []


async def test_delete_game_by_instance(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1)
    await db_session.commit()

    assert await repo.delete(game) is True
    await db_session.commit()
    assert await repo.get_by_id(game.id) is None


async def test_get_by_id_without_relations_and_save(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, _, _ = sample_users
    repo = GameRepository(db_session)

    game = await repo.create(creator=u1, games=[Assassination(target_champion_name="Ahri")], status="EN_ATTENTE")
    await db_session.commit()

    shallow = await repo.get_by_id(game.id, load_relations=False)
    assert shallow is not None
    assert shallow.id == game.id
    assert shallow.status == "EN_ATTENTE"

    # Modification et sauvegarde via save()
    shallow.riot_match_id = "EUW1_999"
    shallow.status = GameStatus.EN_COURS.value
    saved = await repo.save(shallow)
    await db_session.commit()

    assert saved.riot_match_id == "EUW1_999"
    reloaded = await repo.get_by_id(game.id)
    assert reloaded is not None
    assert reloaded.status == GameStatus.EN_COURS.value
    assert reloaded.riot_match_id == "EUW1_999"
    assert len(reloaded.mini_games) == 1
    assert isinstance(reloaded.mini_games[0], Assassination)
    assert reloaded.mini_games[0].target_champion_name == "Ahri"


async def test_active_game_ignores_finished_and_cancelled(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, u2, _ = sample_users
    repo = GameRepository(db_session)

    finished = await repo.create(creator=u1, status=GameStatus.TERMINEE)
    await repo.add_participant(finished, u2)
    cancelled = await repo.create(creator=u1, status=GameStatus.ANNULEE)
    await repo.add_participant(cancelled, u2)
    await db_session.commit()

    assert await repo.get_active_game_for_user(u1.discord_id) is None
    assert await repo.get_active_game_for_user(u2.discord_id) is None

    running = await repo.create(creator=u1, status=GameStatus.EN_COURS)
    await db_session.commit()

    active = await repo.get_active_party_for_user(u1.discord_id)
    assert active is not None
    assert active.id == running.id


async def test_edge_cases_and_aliases(db_session: AsyncSession, sample_users: tuple[User, User, User]):
    u1, u2, u3 = sample_users
    repo = GameRepository(db_session)

    assert PartyRepository is GameRepository
    assert await repo.get_games_by_status(GameStatus.ANNULEE) == []
    assert await repo.get_parties_by_status(GameStatus.EN_ATTENTE) == []
    assert await repo.add_participant("unknown-game", u2) is None
    assert await repo.remove_participant("unknown-game", u2.discord_id) is None
    assert await repo.update_status("unknown-game", GameStatus.EN_COURS) is None

    game = await repo.create(creator=u1)
    await db_session.commit()

    # Scores initiaux à 0
    assert await repo.get_participant_scores(game.id) == {u1.discord_id: 0}

    # Retrait d'un utilisateur non participant (sans erreur)
    same_game = await repo.remove_participant(game, u3.discord_id)
    assert same_game is not None
    assert len(same_game.participants) == 1

    # Mise à jour statut via instance + conservation du riot_match_id existant
    await repo.update_status(game, "EN_COURS", riot_match_id="EUW1_KEEP_ME")
    await repo.update_status(game, GameStatus.TERMINEE)
    await db_session.commit()

    reloaded = await repo.get_by_id(game.id)
    assert reloaded is not None
    assert reloaded.status == GameStatus.TERMINEE.value
    assert reloaded.riot_match_id == "EUW1_KEEP_ME"
