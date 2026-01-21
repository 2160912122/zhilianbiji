from pydantic import BaseModel, RootModel  # 新增RootModel（v2）
from datetime import datetime
from typing import Optional,List
# 用户基础模型（仅保留查询/展示需要的字段）
class UserBase(BaseModel):
    username: str
    status: str = "1"  # 状态：1=启用，0=禁用
    role: str = "1"    # 角色：1=普通用户，2=管理员
    register_time: datetime | None = None

# 用户返回模型（用于列表查询）
class User(UserBase):
    id: int
    class Config:
        # 关键修正：Pydantic V2中 orm_mode → from_attributes
        from_attributes = True

# 用户统计模型（工作台数据展示）
class UserCount(BaseModel):
    total: int
    today_count: int

# 状态更新模型（核心：修改用户状态用）
class UserStatusUpdate(BaseModel):
    status: str


# 2. 新增模型（适配Pydantic v2，极简版）
class UserDateCount(BaseModel):  # 适配按日期查count
    count: int

class UserGrowth(BaseModel):  # 单条增长数据
    date: str
    count: int