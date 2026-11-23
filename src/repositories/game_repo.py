from __future__ import annotations

from typing import Sequence
from sqlalchemy import select, update, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.Game import Game, game_participants
from src.models.User import User
from src.models.MiniGame import MiniGame
from src.models.enums import GameStatus, StatutPartie


class GameRepository:
    """Repository gérant l'agrégat Game (parties/jeux, participants et mini-jeux)."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, game_id: str, load_relations: bool = True) -> Game | None:
        """Récupère une partie/jeu par son identifiant, avec ou sans ses relations."""
        if not load_relations:
            return await self.session.get(Game, game_id)

        stmt = (
            select(Game)
            .where(Game.id == game_id)
            .options(
                selectinload(Game.creator),
                selectinload(Game.participants),
                selectinload(Game.mini_games),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, game: Game) -> Game:
        """Sauvegarde ou met à jour une partie/jeu (et ses mini-jeux en cascade)."""
        game = await self.session.merge(game)
        return game

    async def create(
        self,
        creator: User,
        mini_games: list[MiniGame] | None = None,
        games: list[MiniGame] | None = None,
        status: GameStatus | str = GameStatus.EN_ATTENTE,
    ) -> Game:
        """Crée une nouvelle partie/jeu avec son créateur inscrit comme premier participant."""
        status_val = status.value if isinstance(status, GameStatus) else status
        game = Game(
            status=status_val,
            creator=creator,
            participants=[creator],
            mini_games=mini_games or games or [],
        )
        self.session.add(game)
        return game

    async def get_games_by_status(self, status: str | GameStatus) -> list[Game]:
        """Récupère toutes les parties ayant un statut donné (ex: EN_ATTENTE pour la boucle de 30s)."""
        status_val = status.value if isinstance(status, GameStatus) else status
        stmt = (
            select(Game)
            .where(Game.status == status_val)
            .options(
                selectinload(Game.creator),
                selectinload(Game.participants),
                selectinload(Game.mini_games),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Alias rétrocompatible
    get_parties_by_status = get_games_by_status

    async def get_active_game_for_user(self, discord_id: str) -> Game | None:
        """Recherche si un joueur est déjà dans une partie active (EN_ATTENTE ou EN_COURS)."""
        stmt = (
            select(Game)
            .outerjoin(Game.participants)
            .where(
                or_(
                    Game.creator_id == discord_id,
                    User.discord_id == discord_id,
                ),
                Game.status.in_([GameStatus.EN_ATTENTE.value, GameStatus.EN_COURS.value]),
            )
            .options(
                selectinload(Game.creator),
                selectinload(Game.participants),
                selectinload(Game.mini_games),
            )
            .distinct()
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Alias rétrocompatible
    get_active_party_for_user = get_active_game_for_user

    async def add_participant(self, game_or_id: Game | str, user: User) -> Game | None:
        """Ajoute un joueur aux participants de la partie."""
        game = game_or_id if isinstance(game_or_id, Game) else await self.get_by_id(game_or_id)
        if not game:
            return None

        if not any(p.discord_id == user.discord_id for p in game.participants):
            game.participants.append(user)
        return game

    async def remove_participant(self, game_or_id: Game | str, discord_id: str) -> Game | None:
        """Retire un joueur des participants (kick par le créateur ou abandon)."""
        game = game_or_id if isinstance(game_or_id, Game) else await self.get_by_id(game_or_id)
        if not game:
            return None

        game.participants = [p for p in game.participants if p.discord_id != discord_id]
        return game

    async def update_status(
        self,
        game_or_id: Game | str,
        status: str | GameStatus,
        riot_match_id: str | None = None,
    ) -> Game | None:
        """Met à jour le statut de la partie et optionnellement l'ID de match Riot."""
        game = game_or_id if isinstance(game_or_id, Game) else await self.get_by_id(game_or_id)
        if not game:
            return None

        status_val = status.value if isinstance(status, GameStatus) else status
        game.status = status_val
        if riot_match_id is not None:
            game.riot_match_id = riot_match_id
        return game

    async def set_participant_score(self, game_id: str, discord_id: str, score: int) -> bool:
        """Met à jour le score d'un joueur pour ce match dans game_participants."""
        stmt = (
            update(game_participants)
            .where(
                game_participants.c.game_id == game_id,
                game_participants.c.user_discord_id == discord_id,
            )
            .values(match_score=score)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_participant_scores(self, game_id: str) -> dict[str, int]:
        """Récupère les scores de match de tous les participants d'une partie."""
        stmt = (
            select(game_participants.c.user_discord_id, game_participants.c.match_score)
            .where(game_participants.c.game_id == game_id)
        )
        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def delete(self, game_or_id: Game | str) -> bool:
        """Supprime une partie (ex: annulation par le créateur)."""
        game = game_or_id if isinstance(game_or_id, Game) else await self.session.get(Game, game_or_id)
        if game:
            await self.session.delete(game)
            return True
        return False


# Alias rétrocompatible
PartyRepository = GameRepository

__all__ = ["GameRepository", "PartyRepository"]
