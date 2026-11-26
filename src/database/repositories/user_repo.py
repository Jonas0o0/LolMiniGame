from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_discord_id(self, discord_id: str) -> User | None:
        return await self.session.get(User, discord_id)

    async def get_by_puuid(self, puuid: str) -> User | None:
        stmt = select(User).where(User.riot_puuid == puuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        user = await self.session.merge(user)
        return user

    async def add_score(self, discord_id: str, points: int) -> User | None:
        user = await self.get_by_discord_id(discord_id)
        if user:
            user.global_score += points
        return user

    async def get_leaderboard(self, limit: int = 10) -> list[User]:
        stmt = select(User).order_by(desc(User.global_score)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())