# features/tagging/routes.py
from flask import Blueprint, abort, jsonify, request
from models import Note, db

bp = Blueprint("tagging", __name__, url_prefix="/tag")


@bp.route("/add", methods=["POST"])
def add_tag():
    """
    请求体示例:
    {
        "note_id": 1,
        "tag": "python"
    }
    """
    data = request.get_json()
    note_id = data.get("note_id")
    tag = data.get("tag", "").strip()
    if not note_id or not tag:
        abort(400, description="参数缺失")
    note = Note.query.get_or_404(note_id)

    # 处理逗号分隔的标签集合
    tags = set(filter(None, (note.tags or "").split(",")))
    tags.add(tag)
    note.tags = ",".join(tags)
    db.session.commit()
    return jsonify({"msg": "标签已添加", "tags": list(tags)})


@bp.route("/list/<int:note_id>", methods=["GET"])
def list_tags(note_id):
    note = Note.query.get_or_404(note_id)
    tags = note.tags.split(",") if note.tags else []
    return jsonify({"note_id": note_id, "tags": tags})
