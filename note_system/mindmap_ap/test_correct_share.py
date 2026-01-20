import sys
import os
from datetime import datetime, timedelta, timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入app和db实例
from app import app, db
from app import ShareLink

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

def test_share_timezone():
    with app.app_context():
        print("=== 分享功能时区测试 ===")
        
        # 创建测试用户和文档
        user_id = "test_user_timezone"
        note_id = 1  # 使用现有文档ID
        
        try:
            # 清除之前的测试数据（如果有）
            ShareLink.query.filter_by(token='test_token_timezone').delete()
            db.session.commit()
            
            # 测试1分钟过期
            print("\n1. 测试1分钟过期分享:")
            response = app.test_client().post('/api/share', json={
                'note_id': note_id,
                'permission': 'edit',
                'expire_at': '1m'
            }, headers={'X-User-Id': user_id})
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")
                
                # 检查返回的expire_at格式
                expire_at_str = data['expire_at']
                print(f"   返回的expire_at: {expire_at_str}")
                
                # 验证expire_at包含时区信息
                if '+00:00' in expire_at_str:
                    print("   ✓ 返回的时间包含UTC时区信息")
                
                # 前端显示效果
                local_display = formatDate(expire_at_str)
                print(f"   前端本地时间显示: {local_display}")
                
                # 解析为UTC时间
                utc_dt = datetime.fromisoformat(expire_at_str)
                print(f"   解析的UTC时间: {utc_dt}")
                
                # 检查时间差是否为1分钟
                now_utc = datetime.now(timezone.utc)
                time_diff = utc_dt - now_utc
                print(f"   UTC时间差: {time_diff.seconds}秒")
                
                if 55 < time_diff.seconds < 65:
                    print("   ✓ 过期时间正确设置为1分钟后")
            else:
                print(f"   创建失败: {response.status_code} - {response.get_json()}")
            
            # 测试1天过期
            print("\n2. 测试1天过期分享:")
            response = app.test_client().post('/api/share', json={
                'note_id': note_id,
                'permission': 'view',
                'expire_at': '1d'
            }, headers={'X-User-Id': user_id})
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   创建成功: {data}")
                
                # 检查返回的expire_at格式
                expire_at_str = data['expire_at']
                print(f"   返回的expire_at: {expire_at_str}")
                
                # 前端显示效果
                local_display = formatDate(expire_at_str)
                print(f"   前端本地时间显示: {local_display}")
                
                # 检查时间差是否为1天
                utc_dt = datetime.fromisoformat(expire_at_str)
                now_utc = datetime.now(timezone.utc)
                time_diff = utc_dt - now_utc
                print(f"   UTC时间差: {time_diff.days}天 {time_diff.seconds}秒")
                
                if time_diff.days == 0 and 86300 < time_diff.seconds < 86500:
                    print("   ✓ 过期时间正确设置为1天后")
            else:
                print(f"   创建失败: {response.status_code} - {response.get_json()}")
                
            print("\n=== 测试完成 ===")
            
        finally:
            # 清理测试数据
            ShareLink.query.filter_by(token='test_token_timezone').delete()
            db.session.commit()

if __name__ == "__main__":
    test_share_timezone()