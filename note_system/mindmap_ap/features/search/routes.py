# features/search/routes.py
from flask import Blueprint, request, jsonify
from models import Note

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/', methods=['GET'])
def search():
    """
    URL 参数:
    q   → 关键字（匹配标题或内容）
    tag → 可选标签过滤
    """
    kw = request.args.get('q', '').strip()
    tag = request.args.get('tag', '').strip()

    query = Note.query
    if kw:
        like = f"%{kw}%"
        query = query.filter(
            (Note.title.ilike(like)) |
            (Note.content.ilike(like))
        )
    if tag:
        query = query.filter(Note.tags.ilike(f"%{tag}%"))

    notes = query.order_by(Note.updated_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])
