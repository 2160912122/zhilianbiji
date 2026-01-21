# app/models/note.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# 确保整个项目中只有一个Base实例（关键！）
Base = declarative_base()


class Note(Base):
    __tablename__ = "note"  # 表名
    __table_args__ = {'extend_existing': True}  # 添加这行，允许重定义

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=True)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))  # 若关联用户表，需确保user表已定义