import requests
import sys
import datetime

# APIのベースURL
BASE_URL = "http://127.0.0.1:8000"

def borrow_item(item_id, username, due_date, reason):
    """指定したIDの物品を借りる (パスワード不要)"""
    url = f"{BASE_URL}/api/v1/items/{item_id}/borrow"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "due_date": due_date,
        "lending_reason": reason,
        "lending_location": "東京オフィス (Sample)"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        item = response.json()
        print(f"成功: {item['name']} を借りました。 (返却期限: {item['due_date']})")
    except requests.exceptions.HTTPError as e:
        print(f"貸出エラー ({e.response.status_code}): {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"通信エラー: {e}")

if __name__ == "__main__":
    # 実際には対象のitem_idを何らかの方法で知っている必要があります
    # ここでは例として ID=2 の物品を借ります
    TARGET_ITEM_ID = 2
    
    # ユーザー情報 (パスワード不要、ユーザー名のみ)
    USERNAME = "admin" 
    
    # 返却日 (1週間後)
    due_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    
    print(f"--- 貸出処理開始 (Item ID: {TARGET_ITEM_ID}) ---")
    borrow_item(TARGET_ITEM_ID, USERNAME, due_date, "プロジェクト利用のため")
