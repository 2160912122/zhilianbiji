import os
import sys
from datetime import datetime, timedelta, timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import Share

app = create_app()


# 模拟前端的formatDate函数
def formatDate(isoString):
    if not isoString:
        return "永不过期"
    try:
        # 创建带时区的datetime对象
        utc_dt = datetime.fromisoformat(isoString)
        # 转换为本地时间
        local_dt = utc_dt.astimezone()
        # 格式化显示
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"格式化日期错误: {e}")
        return isoString


def test_timezone_fix():
    with app.app_context():
        print("=== 测试时区修复 ===")

        # 创建测试用户和文档
        user_id = "test_user_timezone"
        doc_id = "test_doc_timezone"
        token = "test_token_timezone"

        try:
            # 测试1分钟过期
            print("\n1. 测试1分钟过期:")
            response = app.test_client().post(
                "/api/share/create",
                json={"doc_id": doc_id, "permission": "view", "expire_at": "1m"},
                headers={"X-User-Id": user_id},
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")

                # 验证返回的expire_at包含时区信息
                expire_at_str = data["expire_at"]
                print(f"   返回的expire_at: {expire_at_str}")

                # 解析并转换为本地时间
                local_time = formatDate(expire_at_str)
                print(f"   本地时间显示: {local_time}")

                # 获取数据库中的记录进行比较
                share = Share.query.filter_by(token=token).first()
                if share:
                    db_expire_at = share.expire_at
                    print(f"   数据库存储时间: {db_expire_at} (无时区)")

                    # 转换数据库时间为UTC时区字符串
                    db_utc_str = datetime.combine(
                        db_expire_at.date(), db_expire_at.time(), tzinfo=timezone.utc
                    ).isoformat()
                    db_local_time = formatDate(db_utc_str)
                    print(f"   数据库时间本地显示: {db_local_time}")
            else:
                print(f"   创建失败: {response.status_code} - {response.get_json()}")

            # 测试1天过期
            print("\n2. 测试1天过期:")
            response = app.test_client().post(
                "/api/share/create",
                json={"doc_id": doc_id, "permission": "edit", "expire_at": "1d"},
                headers={"X-User-Id": user_id},
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")

                # 验证返回的expire_at包含时区信息
                expire_at_str = data["expire_at"]
                print(f"   返回的expire_at: {expire_at_str}")

                # 解析并转换为本地时间
                local_time = formatDate(expire_at_str)
                print(f"   本地时间显示: {local_time}")
        finally:
            # 清理测试数据
            Share.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_timezone_fix()
