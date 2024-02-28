from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Peer(Base):
    __tablename__ = 'peer'

    id = Column(Integer, primary_key=True)
    school_user_id = Column(String, nullable=False)
    tribe = Column(String, nullable=False)
    login = Column(String, nullable=False)
    is_subscribe = Column(Boolean, default=True)
    telegram_id = Column(Integer)
    key = Column(String, nullable=False)
    is_student = Column(Boolean, default=True)
