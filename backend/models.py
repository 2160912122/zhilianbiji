from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from sqlalchemy.orm import relationship
import re

# 初始化数据库和加密工具（避免重复导入）
db = SQLAlchemy()
bcrypt = Bcrypt()


def generate_unique_name(base_name, existing_names):
    """生成唯一的名称，如果存在重复则添加递增数字"""
    if base_name not in existing_names:
        return base_name

    pattern = re.compile(r'^(.*?)\s*\((\d+)\)$')
    counter = 1

    for name in existing_names:
        match = pattern.match(name)
        if match and match.group(1).strip() == base_name:
            num = int(match.group(2))
            if num >= counter:
                counter = num + 1

    new_name = f"{base_name} ({counter})"
    if new_name not in existing_names:
        return new_name

    while True:
        counter += 1
        new_name = f"{base_name} ({counter})"
        if new_name not in existing_names:
            return new_name


# -------------------------- 核心模型：用户（含管理员权限） --------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    # 管理员标识：True=管理员，False=普通用户（适配数据库字段，默认普通用户）
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)

    # 关联各类内容模型（级联删除：用户删除则内容也删除）
    notes = relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')
    categories = relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    tags = relationship('Tag', backref='user', lazy=True, cascade='all, delete-orphan')
    flowcharts = relationship('Flowchart', backref='author', lazy=True, cascade='all, delete-orphan')
    # 【关键修复】关联的是TableDocument（而非Table），解决app.py导入Table报错问题
    tables = relationship('TableDocument', backref='author', lazy=True, cascade='all, delete-orphan')
    whiteboards = relationship('Whiteboard', backref='author', lazy=True, cascade='all, delete-orphan')
    mindmaps = relationship('Mindmap', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """设置加密密码"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """转换为字典（适配前端返回格式）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            # 布尔值转int：1=管理员，0=普通用户（前端易处理）
            'is_admin': 1 if self.is_admin else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


# -------------------------- 分类/标签模型 --------------------------
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    notes = relationship('Note', back_populates='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# -------------------------- 多对多关联表 --------------------------
# 笔记-标签关联
note_tag = db.Table('note_tag',
                    db.Column('note_id', db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
                    )

# 流程图-标签关联
flowchart_tag = db.Table('flowchart_tag',
                         db.Column('flowchart_id', db.Integer, db.ForeignKey('flowchart.id', ondelete='CASCADE'),
                                   primary_key=True),
                         db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
                         )


# -------------------------- 笔记相关模型 --------------------------
class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), nullable=False, default='richtext')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_public = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True)

    category = relationship('Category', back_populates='notes')
    tags = relationship('Tag', secondary=note_tag, backref='notes')
    versions = relationship('NoteVersion', backref='note', lazy='dynamic', cascade='all, delete-orphan')
    share_links = relationship('ShareLink', backref='note', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_content=False):
        result = {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tag_ids': [tag.id for tag in self.tags]
        }
        if include_content:
            result['content'] = self.content
        return result

    def to_full_dict(self):
        result = self.to_dict(include_content=True)
        result['category'] = self.category.to_dict() if self.category else None
        result['tags'] = []
        try:
            for tag in self.tags:
                result['tags'].append(tag.to_dict())
        except Exception as e:
            print(f"Error converting tags to dict: {e}")
        return result

    def save_version(self, updater_id):
        """保存笔记历史版本"""
        version = NoteVersion(
            note_id=self.id,
            content=self.content or '',
            updater_id=updater_id
        )
        db.session.add(version)
        return version


class NoteVersion(db.Model):
    __tablename__ = 'note_version'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updater_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    updater = relationship('User', backref='version_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'updater': {
                'username': self.updater.username if self.updater else '未知用户'
            },
            'updated_at': self.updated_at.isoformat(),
            'content_preview': self.content[:150] + '...' if len(self.content) > 150 else self.content
        }


class ShareLink(db.Model):
    __tablename__ = 'share_link'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), nullable=True)
    flowchart_id = db.Column(db.Integer, db.ForeignKey('flowchart.id', ondelete='CASCADE'), nullable=True)
    mindmap_id = db.Column(db.Integer, db.ForeignKey('mindmap.id', ondelete='CASCADE'), nullable=True)
    token = db.Column(db.String(36), unique=True, nullable=False)
    permission = db.Column(db.String(10), nullable=False, default='view')
    created_at = db.Column(db.DateTime, default=datetime.now)
    expire_at = db.Column(db.DateTime, nullable=True)


# -------------------------- 流程图相关模型 --------------------------
class Flowchart(db.Model):
    __tablename__ = 'flowchart'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    flow_data = db.Column(db.JSON, nullable=True)
    thumbnail = db.Column(db.Text, nullable=True)
    share_token = db.Column(db.String(36), unique=True, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    tags = relationship('Tag', secondary=flowchart_tag, backref='flowcharts', lazy='dynamic')
    share_links = relationship('ShareLink', backref='flowchart', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'flow_data': self.flow_data,
            'thumbnail': self.thumbnail,
            'share_token': self.share_token,
            'is_public': self.is_public,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def save_version(self, updater_id):
        """保存流程图历史版本"""
        version = FlowchartVersion(
            flowchart_id=self.id,
            flow_data=self.flow_data,
            updater_id=updater_id
        )
        db.session.add(version)
        return version


class FlowchartVersion(db.Model):
    __tablename__ = 'flowchart_version'
    id = db.Column(db.Integer, primary_key=True)
    flowchart_id = db.Column(db.Integer, db.ForeignKey('flowchart.id', ondelete='CASCADE'), nullable=False)
    flow_data = db.Column(db.JSON, nullable=True)
    updater_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    updater = relationship('User', backref='flowchart_version_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'flow_data': self.flow_data,
            'updater': {
                'username': self.updater.username if self.updater else '未知用户'
            },
            'updated_at': self.updated_at.isoformat()
        }


# -------------------------- 表格相关模型（关键：类名是TableDocument） --------------------------
class TableDocument(db.Model):
    __tablename__ = 'table_document'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    columns_data = db.Column(db.JSON, nullable=True)
    rows_data = db.Column(db.JSON, nullable=True)
    cell_styles = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'columns': self.columns_data,
            'rows': self.rows_data,
            'cellStyles': self.cell_styles,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def save_version(self, updater_id):
        """保存表格历史版本"""
        version = TableDocumentVersion(
            table_document_id=self.id,
            columns_data=self.columns_data,
            rows_data=self.rows_data,
            cell_styles=self.cell_styles,
            updater_id=updater_id
        )
        db.session.add(version)
        return version


class TableDocumentVersion(db.Model):
    __tablename__ = 'table_document_version'
    id = db.Column(db.Integer, primary_key=True)
    table_document_id = db.Column(db.Integer, db.ForeignKey('table_document.id', ondelete='CASCADE'), nullable=False)
    columns_data = db.Column(db.JSON, nullable=True)
    rows_data = db.Column(db.JSON, nullable=True)
    cell_styles = db.Column(db.JSON, nullable=True)
    updater_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    updater = relationship('User', backref='table_document_version_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'columns': self.columns_data,
            'rows': self.rows_data,
            'cellStyles': self.cell_styles,
            'updater': {
                'username': self.updater.username if self.updater else '未知用户'
            },
            'updated_at': self.updated_at.isoformat()
        }


# -------------------------- 白板相关模型 --------------------------
class Whiteboard(db.Model):
    __tablename__ = 'whiteboard'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    room_key = db.Column(db.String(100), nullable=True)
    data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'room_key': self.room_key,
            'data': self.data,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def save_version(self, updater_id):
        """保存白板历史版本"""
        version = WhiteboardVersion(
            whiteboard_id=self.id,
            data=self.data,
            updater_id=updater_id
        )
        db.session.add(version)
        return version


class WhiteboardVersion(db.Model):
    __tablename__ = 'whiteboard_version'
    id = db.Column(db.Integer, primary_key=True)
    whiteboard_id = db.Column(db.Integer, db.ForeignKey('whiteboard.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    updater_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    updater = relationship('User', backref='whiteboard_version_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data,
            'updater': {
                'username': self.updater.username if self.updater else '未知用户'
            },
            'updated_at': self.updated_at.isoformat()
        }


# -------------------------- 脑图相关模型 --------------------------
class Mindmap(db.Model):
    __tablename__ = 'mindmap'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    share_token = db.Column(db.String(36), unique=True, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    share_links = relationship('ShareLink', backref='mindmap', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'data': self.data,
            'share_token': self.share_token,
            'is_public': self.is_public,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def save_version(self, updater_id):
        """保存脑图历史版本"""
        version = MindmapVersion(
            mindmap_id=self.id,
            data=self.data,
            updater_id=updater_id
        )
        db.session.add(version)
        return version


class MindmapVersion(db.Model):
    __tablename__ = 'mindmap_version'
    id = db.Column(db.Integer, primary_key=True)
    mindmap_id = db.Column(db.Integer, db.ForeignKey('mindmap.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    updater_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now)

    updater = relationship('User', backref='mindmap_version_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data,
            'updater': {
                'username': self.updater.username if self.updater else '未知用户'
            },
            'updated_at': self.updated_at.isoformat()
        }