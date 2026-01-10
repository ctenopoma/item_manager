import requests

# APIのベースURL
BASE_URL = "http://127.0.0.1:8000"

def get_users_list(skip: int = 0, limit: int = 100):
    """
    ユーザーの一覧を取得する (認証不要)
    
    Args:
        skip (int): スキップするユーザー数
        limit (int): 取得するユーザーの上限数
    """
    users_url = f"{BASE_URL}/api/v1/users/?skip={skip}&limit={limit}"
    
    try:
        response = requests.get(users_url)
        response.raise_for_status()
        
        users = response.json()
        print(f"--- ユーザー一覧 ({len(users)}件) ---")
        print(f"{'ユーザー名': <20} | {'表示名': <20} | {'社員ID': <15} | {'メール': <30} | {'部署': <15}")
        print("-" * 110)
        
        for user in users:
            username = user.get('username', '-')
            display_name = user.get('display_name') or '-'
            employee_id = user.get('employee_id') or '-'
            email = user.get('email') or '-'
            department = user.get('department') or '-'
            
            print(f"{username: <20} | {display_name: <20} | {employee_id: <15} | {email: <30} | {department: <15}")
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラーが発生しました: {e.response.status_code}")
        print(f"詳細: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    get_users_list()
