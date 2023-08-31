from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
import settings

engine = create_engine("sqlite:///{}".format(settings.SQLITE_PATH))

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String)
    name = Column(String)
    enabled = Column(Boolean, default=True)
    profile_url = Column(String)

    def __str__(self):
        return f"{self.name}, {self.username}"



Base.metadata.create_all(engine)

session = Session(bind=engine)


def add_profile(telegram_id, username, name, profile_url: str):
    if user := session.query(User).filter_by(telegram_id=telegram_id).first():
        user.username = username or user.username or ''
        user.name = name
    else:
        user = User(telegram_id=telegram_id, username=username or '', name=name, profile_url=profile_url)
        session.add(user)
    session.commit()


def list_users() -> list[User]:
    return list(session.query(User).all())
