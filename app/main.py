from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.database import engine, Base
from app.routers import user, note, auth  # 新增导入auth路由

# 重建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="知行织网-后端接口")

# 注册所有路由（新增auth路由）
app.include_router(note.router)
app.include_router(user.router, prefix="/user")
app.include_router(auth.router)  # 注册/auth路由

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径测试
@app.get("/")
def root():
    return {"msg": "服务正常", "code": 200}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)