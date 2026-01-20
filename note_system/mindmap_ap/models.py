# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

db = SQLAlchemy(metadata=MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}))

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), nullable=False)   # 'richtext' / 'markdown'
    tags = db.Column(db.String(200), nullable=True)   # 逗号分隔的标签
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags.split(',') if self.tags else []
        }

    def to_full_dict(self):
        d = self.to_dict()
        d['content'] = self.content
        return d


class ShareLink(db.Model):
    __tablename__ = 'share_link'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer,
                        db.ForeignKey('note.id', ondelete="CASCADE"),
                        nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False)  # uuid4
    permission = db.Column(db.String(10), nullable=False)  # 'view' / 'edit'
    created_at = db.Column(db.DateTime, default=datetime.now)
    note = db.relationship('Note', backref='share_links')


class NoteHistory(db.Model):
    __tablename__ = 'note_history'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer,
                        db.ForeignKey('note.id', ondelete="CASCADE"),
                        nullable=False)
    content = db.Column(db.Text, nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.now)
    note = db.relationship('Note', backref='histories')
