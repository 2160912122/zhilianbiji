import datetime
from datetime import datetime, timedelta, timezone


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


# 测试时区处理
print("=== 时区处理测试 ===")

# 当前时间
now = datetime.now(timezone.utc)
print(f"当前UTC时间: {now}")
print(f"当前本地时间: {now.astimezone()}")

# 测试1分钟过期
one_minute_later = now + timedelta(minutes=1)
print(f"\n1分钟后UTC时间: {one_minute_later}")

# 测试修复后的输出格式
fixed_iso = one_minute_later.isoformat()
print(f"带时区的ISO字符串: {fixed_iso}")

# 前端解析并显示
local_display = formatDate(fixed_iso)
print(f"前端本地时间显示: {local_display}")

# 测试不带时区的情况（修复前的问题）
naive_time = one_minute_later.replace(tzinfo=None)
naive_iso = naive_time.isoformat()
print(f"\n不带时区的ISO字符串: {naive_iso}")
local_display_naive = formatDate(naive_iso)
print(f"前端解析不带时区的结果: {local_display_naive}")

print("\n=== 测试完成 ===")
