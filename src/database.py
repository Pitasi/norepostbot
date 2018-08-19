"""
    Database interactions
"""
from os import getenv
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine

DB_PATH = getenv('DATABASE', 'sqlite:////tmp/test.db')
_engine = create_engine(DB_PATH)

# Base structure
Base = declarative_base()
class Hash(Base):
    __tablename__ = 'hashes'
    chat_id = Column(Integer, primary_key=True)
    entity_hash = Column(String(64), primary_key=True)
    message_id = Column(String(64), nullable=False)
Base.metadata.create_all(_engine)

_DBSession = sessionmaker(bind=_engine)
_session = _DBSession()

# Actual methods
def get_or_insert(chat_id, entity_hash, message_id):
    """
        First check if the hash is already been stored in db, if so return the
        message_id of the original message; otherwise None is returned and the
        hash stored.
    """
    try:
        result = _session.query(Hash)\
            .filter(and_(
                Hash.chat_id == chat_id,
                Hash.entity_hash == entity_hash,
            ))\
            .one()
        return result.message_id
    except NoResultFound:
        # Hash not found, insert it
        new_hash = Hash(
            chat_id=chat_id,
            entity_hash=entity_hash,
            message_id=message_id
        )
        _session.add(new_hash)
        try:
            _session.commit()
        except Exception:
            _session.rollback()
