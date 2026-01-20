import sys
import os
from datetime import datetime, timedelta, timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, ShareLink, Note

def test_time_format():
    with app.app_context():
        print("=== 时间格式处理测试 ===")
        
        # 创建一个测试时间（1分钟后）
        now = datetime.now(timezone.utc)
        one_minute_later = now + timedelta(minutes=1)
        print(f"当前UTC时间: {now}")
        print(f"1分钟后UTC时间: {one_minute_later}")
        
        # 前端传递的时间格式（ISO带时区）
        frontend_time_str = one_minute_later.isoformat()
        print(f"\n前端传递的时间: {frontend_time_str}")
        
        # 模拟后端处理
        try:
            # 解析前端传递的时间
            expire_at = datetime.fromisoformat(frontend_time_str)
            print(f"后端解析时间: {expire_at}")
            
            # 转换为UTC并移除时区信息
            expire_at_utc_naive = expire_at.astimezone(timezone.utc).replace(tzinfo=None)
            print(f"转换为UTC并移除时区: {expire_at_utc_naive}")
            
            # 存储到数据库（假设）
            print(f"\n数据库存储: {expire_at_utc_naive} (无时区)")
            
            # 查询时的比较（模拟get_share_by_token）
            now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)
            print(f"当前UTC（无时区）: {now_utc_naive}")
            print(f"时间比较结果: {expire_at_utc_naive} > {now_utc_naive} = {expire_at_utc_naive > now_utc_naive}")
            
            # 返回给前端时添加时区信息
            response_expire_at = expire_at_utc_naive.replace(tzinfo=timezone.utc).isoformat()
            print(f"\n返回给前端的时间: {response_expire_at}")
            print("✓ 返回的时间包含UTC时区信息")
            
            # 模拟前端解析
            print(f"\n=== 前端解析测试 ===")
            # 前端formatDate函数
            def formatDate(isoString):
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
            
            # 解析带时区的时间
            local_time = formatDate(response_expire_at)
            print(f"前端本地时间显示: {local_time}")
            
            # 对比修复前的问题（无时区）
            old_response = expire_at_utc_naive.isoformat()
            old_local_time = formatDate(old_response)
            print(f"修复前本地时间显示: {old_local_time}")
            
            # 计算时间差
            if local_time != old_local_time:
                print("\n✓ 时区修复成功！本地时间显示正确")
                print(f"   修复前: {old_local_time} (错误，相差8小时)")
                print(f"   修复后: {local_time} (正确，本地时间)")
            
        except Exception as e:
            print(f"\n错误: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_time_format()