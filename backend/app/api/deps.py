from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance FastAPI pour fournir une session de base de données asynchrone.
    Garantit la fermeture de la session après chaque requête.
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
