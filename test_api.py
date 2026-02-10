# 测试智谱AI API调用
import os
from zhipuai import ZhipuAI

# 从环境变量获取API密钥
api_key = "c547d010d8824a0891001c1a050e3405.qKcfLi1KNuzwotQ3"

print(f"使用API密钥: {api_key}")

# 初始化客户端
client = ZhipuAI(api_key=api_key)

# 测试API调用
try:
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": "你好，测试一下API调用"}
        ],
        temperature=0.7,
        max_tokens=2048
    )
    print("API调用成功!")
    print(f"响应: {response}")
except Exception as e:
    print(f"API调用失败: {str(e)}")
    import traceback
    traceback.print_exc()