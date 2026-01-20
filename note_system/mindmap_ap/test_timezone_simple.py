from datetime import datetime, timedelta, timezone

# 模拟数据库中的UTC时间
db_time = datetime(2026, 1, 16, 2, 31, 0)  # 数据库中存储的UTC时间，不带时区信息

# 测试1：直接使用不带时区的时间进行strftime格式化
print("=== 测试1：不带时区信息的时间处理 ===")
print(f"数据库原始时间: {db_time}")
print(f"直接strftime格式化: {db_time.strftime('%Y-%m-%d %H:%M')}")

# 测试2：添加UTC时区信息后的处理
print("\n=== 测试2：添加UTC时区信息后的处理 ===")
db_time_with_tz = db_time.replace(tzinfo=timezone.utc)
print(f"带UTC时区的时间: {db_time_with_tz}")
print(f"直接strftime格式化: {db_time_with_tz.strftime('%Y-%m-%d %H:%M')}")
print(
    f"转换为本地时间后格式化: {db_time_with_tz.astimezone().strftime('%Y-%m-%d %H:%M')}"
)

# 测试3：模拟不同时区的转换
print("\n=== 测试3：不同时区转换测试 ===")
import pytz

shanghai_tz = pytz.timezone("Asia/Shanghai")
print(
    f"转换为上海时间: {db_time_with_tz.astimezone(shanghai_tz).strftime('%Y-%m-%d %H:%M')}"
)
new_york_tz = pytz.timezone("America/New_York")
print(
    f"转换为纽约时间: {db_time_with_tz.astimezone(new_york_tz).strftime('%Y-%m-%d %H:%M')}"
)

# 测试4：模拟模板中的astimezone()调用
print("\n=== 测试4：模板中的astimezone()调用模拟 ===")
template_result = db_time_with_tz.astimezone().strftime("%Y-%m-%d %H:%M")
print(
    f"模板中使用{{% expire_at.astimezone().strftime('%Y-%m-%d %H:%M') %}}的结果: {template_result}"
)

# 总结
print("\n=== 总结 ===")
print("1. 数据库存储的时间不带时区信息")
print("2. 我们需要手动添加UTC时区信息")
print("3. 在模板中使用astimezone()可以将UTC时间转换为用户本地时间")
print(
    f"4. 对于UTC时间{db_time.strftime('%Y-%m-%d %H:%M')}，用户将看到: {template_result}"
)
