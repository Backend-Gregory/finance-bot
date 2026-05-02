from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from datetime import datetime

engine = create_engine("sqlite+pysqlite:///database.db")

Session = sessionmaker(bind=engine)
session = Session()

class Base(DeclarativeBase):
    pass

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    note: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

def init_db():
    Base.metadata.create_all(engine)