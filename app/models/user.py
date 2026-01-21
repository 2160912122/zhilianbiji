from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "user"  # 与数据库表名一致

    # 完全匹配数据库的字段
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    register_time = Column(DateTime, default=func.now())  # 用数据库已有的register_time
    status = Column(Integer, default=1)
    role = Column(Integer, default=2)