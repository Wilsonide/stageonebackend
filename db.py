from datetime import UTC, datetime

from sqlalchemy import JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import config

engine = create_engine(config.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class StringRecord(Base):
    __tablename__ = "strings_record"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    value: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    properties: Mapped[dict] = mapped_column(JSON)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
