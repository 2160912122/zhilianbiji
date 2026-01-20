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


def test_complete_share():
    with app.app_context():
        print("=== 完整分享功能测试 ===")

        # 创建测试用户和文档
        user_id = "test_user_final"
        doc_id = "test_doc_final"

        try:
            # 清除之前的测试数据
            Share.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            # 测试1分钟过期
            print("\n1. 测试1分钟过期分享:")
            response = app.test_client().post(
                "/api/share/create",
                json={"doc_id": doc_id, "permission": "edit", "expire_at": "1m"},
                headers={"X-User-Id": user_id},
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")

                token = data["share_url"].split("/")[-1]
                expire_at_str = data["expire_at"]
                print(f"   返回的token: {token}")
                print(f"   返回的expire_at: {expire_at_str}")

                # 前端显示效果
                local_display = formatDate(expire_at_str)
                print(f"   前端本地时间显示: {local_display}")

                # 验证分享链接是否可访问
                share_response = app.test_client().get(f"/api/share/{token}")
                if share_response.status_code == 200:
                    share_data = share_response.get_json()
                    print(f"   分享链接验证成功: {share_data}")
                else:
                    print(f"   分享链接验证失败: {share_response.status_code}")
            else:
                print(f"   创建失败: {response.status_code} - {response.get_json()}")

            # 测试1天过期
            print("\n2. 测试1天过期分享:")
            response = app.test_client().post(
                "/api/share/create",
                json={"doc_id": doc_id, "permission": "view", "expire_at": "1d"},
                headers={"X-User-Id": user_id},
            )

            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")

                token = data["share_url"].split("/")[-1]
                expire_at_str = data["expire_at"]
                print(f"   返回的token: {token}")
                print(f"   返回的expire_at: {expire_at_str}")

                # 前端显示效果
                local_display = formatDate(expire_at_str)
                print(f"   前端本地时间显示: {local_display}")

                # 验证分享链接是否可访问
                share_response = app.test_client().get(f"/api/share/{token}")
                if share_response.status_code == 200:
                    share_data = share_response.get_json()
                    print(f"   分享链接验证成功: {share_data}")
                else:
                    print(f"   分享链接验证失败: {share_response.status_code}")
            else:
                print(f"   创建失败: {response.status_code} - {response.get_json()}")

            print("\n=== 测试完成 ===")

        finally:
            # 清理测试数据
            Share.query.filter_by(user_id=user_id).delete()
            db.session.commit()


if __name__ == "__main__":
    test_complete_share()
