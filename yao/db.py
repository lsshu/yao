import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Column, create_engine, ForeignKey, TIMESTAMP
from sqlalchemy.orm import sessionmaker, relationship, joinedload, subqueryload, Session as sqlalchemySession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mptt import mptt_sessionmaker

import config as user_config

Engine = create_engine(
    user_config.DB_SQLALCHEMY_DATABASE_URL if hasattr(user_config, "DB_SQLALCHEMY_DATABASE_URL") else "sqlite:///db.sqlite3",
    **user_config.DB_ENGINE_KWARGS if hasattr(user_config, "DB_ENGINE_KWARGS") else {
        "connect_args": {
            'check_same_thread': False
        }
    }
)
SessionLocal = sessionmaker(bind=Engine, **user_config.DB_SESSION_MAKER_KWARGS if hasattr(user_config, "DB_SESSION_MAKER_KWARGS") else {
    "autoflush": False,
    "autocommit": False,
    "expire_on_commit": True
})

SessionMpttLocal = mptt_sessionmaker(SessionLocal)
# 创建基本映射类
BaseModel = declarative_base()


def session():
    """
    实例 sessionmaker
    :return:
    """
    _db = SessionLocal()
    try:
        yield _db
    finally:
        try:
            _db.close()
        except:
            pass


def mptt_session():
    """
    实例 sessionmaker
    :return:
    """
    mptt_db = SessionMpttLocal()
    try:
        yield mptt_db
    finally:
        mptt_db.close()


class Model(BaseModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(32), unique=True, nullable=False, default=lambda: uuid.uuid4().hex, comment="UUID")
    deleted_at = Column(TIMESTAMP, index=True, nullable=True, comment="删除日期")
    created_at = Column(TIMESTAMP, nullable=True, default=datetime.now, comment="创建日期")
    updated_at = Column(TIMESTAMP, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新日期")

    def to_dict(self):
        """
        ORM转dict
        :return:
        """
        columns = [c.name for c in self.__table__.columns] + [name for name, obj in vars(self.__class__).items() if isinstance(obj, property)]
        return {key: getattr(self, key, None) for key in columns}
