import requests
import sys

# APIのベースURL
BASE_URL = "http://127.0.0.1:8000"

def return_item(item_id):
    """指定したIDの物品を返却する (認証不要)"""
    url = f"{BASE_URL}/api/v1/items/{item_id}/return"
    
    try:
        response = requests.post(url)
        response.raise_for_status()
        item = response.json()
        print(f"成功: {item['name']} を返却しました。")
    except requests.exceptions.HTTPError as e:
        print(f"返却エラー ({e.response.status_code}): {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"通信エラー: {e}")

if __name__ == "__main__":
    # 実際には対象のitem_idを何らかの方法で知っている必要があります
    # ここでは例として ID=2 の物品を返します
    TARGET_ITEM_ID = 2
    
    print(f"--- 返却処理開始 (Item ID: {TARGET_ITEM_ID}) ---")
    return_item(TARGET_ITEM_ID)
