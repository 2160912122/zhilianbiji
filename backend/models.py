from datetime import datetime
from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    flowcharts = db.relationship('Flowchart', backref='author', lazy=True, cascade='all, delete-orphan')


# 标签模型
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 标签属于特定用户
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    user = db.relationship('User', backref=db.backref('tags', lazy=True))
    flowcharts = db.relationship('Flowchart', secondary='flowchart_tags', back_populates='tags')


# 流程图和标签的关联表（多对多关系）
class FlowchartTag(db.Model):
    __tablename__ = 'flowchart_tags'

    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.Integer, db.ForeignKey('flowcharts.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 唯一约束，确保同一个流程图不会重复添加同一个标签
    __table_args__ = (
        db.UniqueConstraint('flowchart_id', 'tag_id', name='unique_flowchart_tag'),
    )


class Flowchart(db.Model):
    __tablename__ = 'flowcharts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    flow_data = db.Column(db.JSON)
    thumbnail = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 与标签的多对多关系
    tags = db.relationship('Tag', secondary='flowchart_tags', back_populates='flowcharts')