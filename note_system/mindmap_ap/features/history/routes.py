# features/history/routes.py
from flask import Blueprint, request, jsonify, abort
from models import db, Note, NoteHistory

bp = Blueprint('history', __name__, url_prefix='/history')

@bp.route('/save', methods=['POST'])
def save_history():
    """
    前端在每次保存笔记后调用此接口
    {
        "note_id": 1,
        "content": "markdown or html 内容"
    }
    """
    data = request.get_json()
    note_id = data.get('note_id')
    content = data.get('content', '')
    if not note_id:
        abort(400, description='note_id 必填')
    # 确认笔记存在
    Note.query.get_or_404(note_id)

    hist = NoteHistory(note_id=note_id, content=content)
    db.session.add(hist)
    db.session.commit()
    return jsonify({'msg': '历史已保存', 'history_id': hist.id})

@bp.route('/list/<int:note_id>', methods=['GET'])
def list_history(note_id):
    Note.query.get_or_404(note_id)
    histories = (NoteHistory.query
                 .filter_by(note_id=note_id)
                 .order_by(NoteHistory.saved_at.desc())
                 .limit(20)
                 .all())
    return jsonify([{
        'id': h.id,
        'content': h.content,
        'saved_at': h.saved_at.isoformat()
    } for h in histories])
