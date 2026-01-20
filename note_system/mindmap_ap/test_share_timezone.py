from datetime import datetime, timezone
import pytz

# 模拟后端生成带时区的expire_at
expire_at_utc = datetime(2026, 1, 16, 2, 31, 0, tzinfo=timezone.utc)

# 模拟前端的formatDate函数
def formatDate(dateString):
    if not dateString:
        return ''
    try:
        # 尝试直接解析带时区的ISO字符串
        date = datetime.fromisoformat(dateString.replace('Z', '+00:00'))
        # 转换为本地时间后格式化
        local_date = date.astimezone(pytz.timezone('Asia/Shanghai'))
        return local_date.strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"Date parsing error: {e}")
        return ''

# 测试share.html模板中的strftime行为
print("=== 分享页面过期时间显示测试 ===")
print(f"后端生成的带时区expire_at: {expire_at_utc}")
print(f"模板中使用strftime格式化: {expire_at_utc.strftime('%Y-%m-%d %H:%M')}")
print(f"转换为本地时间后格式化: {expire_at_utc.astimezone(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')}")

# 测试带时区的ISO字符串解析
iso_string_with_tz = expire_at_utc.isoformat()
print(f"\n=== 带时区ISO字符串解析测试 ===")
print(f"带时区的ISO字符串: {iso_string_with_tz}")
print(f"前端formatDate函数解析结果: {formatDate(iso_string_with_tz)}")
