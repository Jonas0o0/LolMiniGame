from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    User,
    Game,
    Bingo,
    Assassination,
    BingoCell,
    BingoGrid,
    GameStatus,
)


async def test_create_user(db_session: AsyncSession):
    """Vérifie la création et la récupération d'un User dans la BDD."""
    user = User(
        discord_id="123456789",
        riot_puuid="puuid-faker-kr",
        riot_game_tag="Hide on bush",
        riot_tag_line="KR1",
        global_score=0,
    )
    db_session.add(user)
    await db_session.commit()

    stmt = select(User).where(User.discord_id == "123456789")
    result = await db_session.execute(stmt)
    loaded_user = result.scalar_one()

    assert loaded_user.riot_game_tag == "Hide on bush"
    assert loaded_user.riot_tag_line == "KR1"
    assert loaded_user.global_score == 0


async def test_create_game_with_participants(db_session: AsyncSession):
    """Vérifie la création d'un Game avec son créateur et ses participants (relation Many-to-Many)."""
    faker = User(
        discord_id="1001",
        riot_puuid="puuid-faker",
        riot_game_tag="Hide on bush",
        riot_tag_line="KR1",
        global_score=100,
    )
    caps = User(
        discord_id="1002",
        riot_puuid="puuid-caps",
        riot_game_tag="Caps",
        riot_tag_line="EUW",
        global_score=50,
    )
    db_session.add_all([faker, caps])

    game = Game(
        status=GameStatus.EN_ATTENTE.value,
        creator=faker,
    )
    game.participants.extend([faker, caps])
    db_session.add(game)
    await db_session.commit()

    # Relecture avec chargement eager
    stmt = (
        select(Game)
        .where(Game.id == game.id)
        .options(
            selectinload(Game.creator),
            selectinload(Game.participants),
        )
    )
    result = await db_session.execute(stmt)
    loaded_game = result.scalar_one()

    assert loaded_game.creator.riot_game_tag == "Hide on bush"
    assert len(loaded_game.participants) == 2
    participant_tags = [p.riot_game_tag for p in loaded_game.participants]
    assert "Hide on bush" in participant_tags
    assert "Caps" in participant_tags


async def test_game_with_multiple_mini_games(db_session: AsyncSession):
    """Vérifie qu'un Game peut contenir plusieurs mini-jeux polymorphiques (Bingo et Assassination)."""
    creator = User(
        discord_id="2001",
        riot_puuid="puuid-creator",
        riot_game_tag="Leader",
        riot_tag_line="EUW",
        global_score=0,
    )
    db_session.add(creator)

    game = Game(
        status=GameStatus.EN_COURS.value,
        creator=creator,
    )

    # 1. Mini-jeu Bingo avec grilles JSON
    cell = BingoCell(description="First Blood", riot_stat_to_check="first_blood", target_value=1)
    grid = BingoGrid(player_discord_id=creator.discord_id, cells=[cell])
    bingo = Bingo(
        game_type="BINGO",
        player_grids=[{
            "player_discord_id": grid.player_discord_id,
            "cells": [vars(c) for c in grid.cells],
        }],
    )

    # 2. Mini-jeu Assassination avec cible
    assassination = Assassination(
        game_type="ASSASSINATION",
        target_participant_id=3,
        target_champion_name="Zed",
    )

    # Ajout des deux mini-jeux dans le même jeu
    game.mini_games.extend([bingo, assassination])
    db_session.add(game)
    await db_session.commit()

    # Relecture
    stmt = (
        select(Game)
        .where(Game.id == game.id)
        .options(selectinload(Game.mini_games))
    )
    result = await db_session.execute(stmt)
    loaded_game = result.scalar_one()

    assert len(loaded_game.mini_games) == 2
    game_types = [g.game_type for g in loaded_game.mini_games]
    assert "BINGO" in game_types
    assert "ASSASSINATION" in game_types

    loaded_assassination = next(g for g in loaded_game.mini_games if isinstance(g, Assassination))
    assert loaded_assassination.target_champion_name == "Zed"

    loaded_bingo = next(g for g in loaded_game.mini_games if isinstance(g, Bingo))
    assert loaded_bingo.player_grids is not None
    assert loaded_bingo.player_grids[0]["cells"][0]["description"] == "First Blood"


def test_bingo_dataclasses():
    """Vérifie que les dataclasses BingoCell et BingoGrid s'instancient correctement en pur Python."""
    cell = BingoCell(
        description="Kill 10 minions",
        riot_stat_to_check="totalMinionsKilled",
        target_value=10,
        is_checked=True,
    )
    grid = BingoGrid(player_discord_id="9999", cells=[cell])

    assert cell.description == "Kill 10 minions"
    assert cell.is_checked is True
    assert len(grid.cells) == 1
    assert grid.player_discord_id == "9999"
