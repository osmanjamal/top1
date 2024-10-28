from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class DatabaseManager:
    """
    Database manager for handling database operations.
    """

    @staticmethod
    def get_db() -> Generator[Session, None, None]:
        """
        Get database session.
        """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @staticmethod
    def init_db() -> None:
        """
        Initialize database.
        """
        # Import all models here to ensure they are registered
        from app.models import user, order, position, trade, signal  # noqa: F401

        # Create all tables
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def cleanup_db() -> None:
        """
        Cleanup database connections.
        """
        engine.dispose()

    @staticmethod
    def check_db_connection() -> bool:
        """
        Check database connection.
        """
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            return True
        except Exception:
            return False
        finally:
            db.close()

    @classmethod
    def create_db_tables(cls) -> None:
        """
        Create all database tables.
        """
        Base.metadata.create_all(bind=engine)

    @classmethod
    def drop_db_tables(cls) -> None:
        """
        Drop all database tables.
        """
        Base.metadata.drop_all(bind=engine)

    @staticmethod
    def create_db_backup() -> str:
        """
        Create database backup.
        """
        # Implement backup logic
        return "backup_path"

    @staticmethod
    def restore_db_backup(backup_path: str) -> bool:
        """
        Restore database from backup.
        """
        # Implement restore logic
        return True

    @staticmethod
    def optimize_db() -> None:
        """
        Optimize database performance.
        """
        # Implement optimization logic
        pass