from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Création du moteur asynchrone SQLAlchemy 2.0
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Régler sur True pour le debug SQL
    future=True,
    pool_pre_ping=True
)

# Fabrique de sessions asynchrones
SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)
