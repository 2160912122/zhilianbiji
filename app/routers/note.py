from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import get_db
from app.models.note import Note  # 正确的模型类名是Note
from app.models.user import User
from app.utils.auth import verify_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/note", tags=["笔记管理"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# 管理员权限校验依赖
def get_current_admin(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    return username


@router.get("/type/stat")
def get_note_type_stat(
        db: Session = Depends(get_db),
        admin: str = Depends(get_current_admin)
):
    """获取笔记类型统计"""
    # 按类型分组统计数量（增加空值处理）
    stat = db.query(
        Note.type,
        func.count(Note.id)
    ).group_by(Note.type).all()

    # 处理None类型（避免前端显示异常）
    return [{"type": t or "未分类", "count": c} for t, c in stat]



@router.get("/count")
def get_note_count(
    db: Session = Depends(get_db)
):
    """获取笔记总数"""
    total = db.query(func.count(Note.id)).scalar() or 0
    return {"count": total}


@router.get("/list")
def get_note_list(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
        type: str = Query(None),
        author_id: int = Query(None),
        start_time: datetime = Query(None),
        end_time: datetime = Query(None),
        db: Session = Depends(get_db),
        admin: str = Depends(get_current_admin)
):
    """获取笔记列表（分页+筛选）"""
    # 关联查询：笔记表关联用户表（修复外键字段名，统一用user_id）
    query = db.query(Note, User.username).join(
        User, Note.user_id == User.id, isouter=True  # 左连接，避免无作者的笔记被过滤
    )

    # 筛选条件（增加空值判断，避免查询报错）
    if type is not None:
        query = query.filter(Note.type == type)
    if author_id is not None:
        query = query.filter(Note.user_id == author_id)  # 修正为user_id（匹配常见命名）
    if start_time is not None:
        query = query.filter(Note.create_time >= start_time)
    if end_time is not None:
        query = query.filter(Note.create_time <= end_time)

    # 分页逻辑（先计数，再分页）
    total = query.count()
    notes = query.offset((page - 1) * size).limit(size).all()

    # 格式化返回数据（增加字段判空，避免前端报错）
    result = []
    for note, author_name in notes:
        result.append({
            "id": note.id,
            "title": note.title or "无标题",
            "type": note.type or "未分类",
            "author_id": note.user_id,  # 修正为user_id
            "author_name": author_name or "未知用户",
            "create_time": note.create_time,
            "view_count": getattr(note, "view_count", 0)  # 兼容无view_count字段的情况
        })

    return {
        "list": result,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size  # 新增总页数，方便前端分页
    }