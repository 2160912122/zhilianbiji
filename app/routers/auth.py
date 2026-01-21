from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import authenticate_admin, create_access_token

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """管理员登录接口（接收账号密码，返回Token）"""
    # 打印：接收到的账号密码
    print(f"接收到的用户名：{form_data.username}，密码：{form_data.password}")
    # 验证账号密码（已包含密码验证逻辑）
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成Token
    access_token = create_access_token(data={"sub": admin.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": admin.username
    }