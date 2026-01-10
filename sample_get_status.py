import json

import requests

# APIのベースURL
BASE_URL = "http://127.0.0.1:8000"

def get_items_status():
    """
    物品のステータス一覧を取得する (認証不要)
    """
    url = f"{BASE_URL}/api/v1/items/status"
    try:
        response = requests.get(url)
        response.raise_for_status() # エラーなら例外を発生させる
        
        items = response.json()
        print(f"--- 物品ステータス一覧 ({len(items)}件) ---")
        print(f"{'ID': <5} | {'物品名': <15} | {'ステータス': <10} | {'借用者': <15}")
        print("-" * 55)
        for item in items:
            item_id = item['id']
            status = item['status']
            name = item['name']
            owner = item.get('owner_name') or "なし"
            print(f"{item_id: <5} | {name: <15} | {status: <10} | {owner: <15}")
            
    except requests.exceptions.RequestException as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    get_items_status()
