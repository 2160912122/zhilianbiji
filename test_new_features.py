import requests
import json

def test_ai_search():
    print("=== 测试生成式智能搜索接口 ===")
    
    # 登录获取token
    login_url = "http://localhost:5000/api/login"
    login_data = {"username": "testuser", "password": "testpass"}
    
    try:
        login_response = requests.post(login_url, json=login_data)
        login_result = login_response.json()
        
        if login_result.get('code') != 200:
            print("登录失败")
            return
        
        token = login_result['data']['token']
        print(f"获取到token: {token[:30]}...")
        
        # 测试AI搜索接口
        search_url = "http://localhost:5000/api/search/ai"
        headers = {'Authorization': f'Bearer {token}'}
        search_data = {"query": "Python代码示例"}
        
        print("\n测试AI搜索...")
        response = requests.post(search_url, headers=headers, json=search_data)
        print(f"状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('code') == 200:
                data = result.get('data', {})
                print(f"\n搜索查询: {data.get('query')}")
                print(f"本地结果数量: {len(data.get('local_results', []))}")
                print(f"AI可用: {data.get('ai_enabled')}")
                if data.get('ai_answer'):
                    print(f"AI回答长度: {len(data['ai_answer'])}")
            
        except ValueError:
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_search()
