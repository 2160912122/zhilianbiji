from app import app
from models import db, Note

with app.app_context():
    # 获取所有笔记并按创建时间排序
    all_notes = Note.query.order_by(Note.created_at).all()
    print(f"原始笔记数量: {len(all_notes)}")
    
    # 只保留最早的一个笔记，删除其他重复的
    if len(all_notes) > 1:
        # 保留最早的笔记
        notes_to_keep = all_notes[0]
        notes_to_delete = all_notes[1:]
        
        print(f"保留笔记: ID={notes_to_keep.id}, 标题={notes_to_keep.title}, 创建时间={notes_to_keep.created_at}")
        print(f"删除 {len(notes_to_delete)} 个重复笔记")
        
        # 删除重复笔记
        for note in notes_to_delete:
            db.session.delete(note)
        
        db.session.commit()
        print("清理完成！")
    else:
        print("没有重复笔记需要清理")
    
    # 检查清理后的结果
    remaining_notes = Note.query.all()
    print(f"清理后笔记数量: {len(remaining_notes)}")
    for note in remaining_notes:
        print(f"剩余笔记: ID={note.id}, 标题={note.title}, 创建时间={note.created_at}")