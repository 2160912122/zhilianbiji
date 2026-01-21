from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
# 核心：给date起别名dt_date，全程使用该别名
from datetime import date as dt_date, timedelta, datetime
from typing import Optional, List
from app.models.user import User as UserModel
from app.schemas.user import (
    User, UserCount, UserStatusUpdate,
    UserDateCount, UserGrowth
)
from app.database import get_db

router = APIRouter()


# 1. 用户列表接口（保留原有逻辑）
@router.get("/list", response_model=list[User], tags=["用户管理"])
def get_user_list(
        db: Session = Depends(get_db),
        username: str = None,
        status: int = None,
        startTime: str = None,
        endTime: str = None
):
    query = db.query(UserModel)

    if username and username.strip():
        query = query.filter(UserModel.username.like(f"%{username.strip()}%"))

    if status is not None:
        query = query.filter(UserModel.status == status)

    if startTime and endTime:
        query = query.filter(
            UserModel.register_time >= startTime,
            UserModel.register_time <= endTime
        )

    users = query.all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "status": str(user.status),
            "role": str(user.role),
            "register_time": user.register_time
        })
    return result


# 2. 修改用户状态接口（保留原有逻辑）
@router.put("/update-status/{user_id}", tags=["用户管理"])
def update_user_status(
        user_id: int,
        status_data: UserStatusUpdate,
        db: Session = Depends(get_db)
):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db_user.status = int(status_data.status)
    db.commit()
    return {"msg": "状态修改成功"}


# 3. 用户统计接口（修复参数名+别名）
@router.get(
    "/count",
    tags=["用户管理"],
    response_model=UserCount | UserDateCount
)
def get_user_count(
    db: Session = Depends(get_db),
    # 新增alias="date"，让前端仍能使用?date=xxx请求
    query_date: Optional[str] = Query(None, alias="date", description="查询日期，格式YYYY-MM-DD")
):
    if query_date:
        try:
            # 转换为date类型（使用dt_date兼容）
            target_date = datetime.strptime(query_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，需为YYYY-MM-DD")
        count = db.query(func.count(UserModel.id)).filter(
            func.date(UserModel.register_time) == target_date
        ).scalar() or 0
        return {"count": count}
    total = db.query(func.count(UserModel.id)).scalar() or 0
    today = dt_date.today()  # 用别名dt_date，避免冲突
    today_count = db.query(func.count(UserModel.id)).filter(
        func.date(UserModel.register_time) == today
    ).scalar() or 0
    return {"total": total, "today_count": today_count}

# 4. 用户增长接口（核心修复：date→dt_date）
@router.get(
    "/growth",
    tags=["用户管理"],
    response_model=List[UserGrowth]
)
def get_user_growth(
    db: Session = Depends(get_db),
    days: int = Query(7, description="查询近N天数据，默认7天")
):
    today = dt_date.today()  # 关键修复：把date.today()改为dt_date.today()
    growth_data = []
    for i in range(days):
        target_date = today - timedelta(days=days - 1 - i)
        date_str = target_date.strftime("%Y-%m-%d")
        count = db.query(func.count(UserModel.id)).filter(
            func.date(UserModel.register_time) == target_date
        ).scalar() or 0
        growth_data.append({"date": date_str, "count": count})
    return growth_data