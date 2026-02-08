from app import app
from models import db, Note, User

with app.app_context():
    print('用户数:', User.query.count())
    print('笔记数:', Note.query.count())
    print('笔记列表:')
    notes = Note.query.all()
    for note in notes:
        print(f'ID: {note.id}, 标题: {note.title}, 用户ID: {note.user_id}, 创建时间: {note.created_at}')
    
    # 检查当前用户(假设ID=1)的笔记
    print('\n当前用户(ID=1)的笔记:')
    user_notes = Note.query.filter_by(user_id=1).all()
    for note in user_notes:
        print(f'ID: {note.id}, 标题: {note.title}')