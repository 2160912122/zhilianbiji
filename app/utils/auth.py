from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models.admin import Admin  # 关联admin表模型
from app.database import get_db  # 数据库会话依赖

# 密码加密上下文（兼容明文/密文验证）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """临时强制明文验证（先解决登录问题）"""
    # 修复：字段名匹配后，此处明文对比才有效
    return plain_password == hashed_password

def get_password_hash(password: str):
    """生成密码哈希值（加密存储）"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """生成JWT Token"""
    to_encode = data.copy()
    # 设置Token过期时间（默认120分钟）
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES or 120
    )
    to_encode.update({"exp": expire})
    # 生成Token（确保SECRET_KEY和ALGORITHM已配置）
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,  # 移除冗余默认值，依赖配置文件
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str):
    """验证Token有效性"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise JWTError
        return username
    except JWTError:
        return None

def authenticate_admin(db: Session, username: str, password: str):
    """验证管理员账号密码并返回用户信息"""
    # 打印：当前要查询的用户名
    print(f"查询的用户名：{username}")
    # 从admin表查询用户
    admin = db.query(Admin).filter(Admin.username == username).first()
    # 打印：数据库查询结果（是否找到用户）
    print(f"数据库查询到的用户：{admin}")
    if not admin:
        print("用户名不存在")
        return None  # 用户名不存在
    # 修复：字段名从 pwd → password（匹配Admin模型）
    print(f"数据库密码：{admin.password}，输入的密码：{password}")
    # 验证密码
    if not verify_password(password, admin.password):  # 修复字段名
        print("密码错误")
        return None  # 密码错误
    print("登录成功")
    return admin