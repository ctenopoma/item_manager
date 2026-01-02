API利用ガイド
=============

このドキュメントでは、Item ManagerのAPI利用方法について説明します。

物品情報の取得
--------------

物品の一覧と現在のステータスを一覧形式で取得するためのAPIです。
Growiや外部ダッシュボードなど、認証なしで物品の状況（貸出中、延滞など）を表示する目的で使用されます。

エンドポイント
~~~~~~~~~~~~~~

.. code-block:: text

   GET /api/v1/items/status

認証
~~~~

不要（パブリックアクセス可能）

リクエストパラメータ
~~~~~~~~~~~~~~~~~~~~

なし

レスポンス
~~~~~~~~~~

以下のフィールドを含むJSON配列が返されます。

* ``name`` (string): 物品名
* ``management_code`` (string): 管理コード
* ``status`` (string): 現在のステータス ("available", "borrowed" など)
* ``owner_name`` (string, optional): 現在の借用者の表示名（貸出中の場合のみ）。未貸出時は ``null``。
* ``due_date`` (string, optional): 返却予定日 (YYYY-MM-DD形式)。
* ``is_overdue`` (boolean): 現在の日付が返却予定日を過ぎているかどうか。
* ``is_fixed_asset`` (boolean): 固定資産かどうか。
* ``accessories`` (array of strings): 付属品のリスト。
* ``lending_reason`` (string, optional): 貸出理由（貸出中の場合）。
* ``lending_location`` (string, optional): 貸出場所（貸出中の場合）。

レスポンス例
~~~~~~~~~~~~

.. code-block:: json

   [
       {
           "name": "ノートPC A",
           "management_code": "PC-001",
           "status": "borrowed",
           "owner_name": "山田 太郎",
           "due_date": "2025-12-31",
           "is_overdue": true,
           "is_fixed_asset": true,
           "accessories": ["ACアダプタ", "マウス"],
           "lending_reason": "出張のため",
           "lending_location": "東京オフィス"
       },
       {
           "name": "プロジェクター",
           "management_code": "PRJ-001",
           "status": "available",
           "owner_name": null,
           "due_date": null,
           "is_overdue": false,
           "is_fixed_asset": false,
           "accessories": ["リモコン", "HDMIケーブル"],
           "lending_reason": null,
           "lending_location": null
       }
   ]


物品の貸出登録
--------------

物品を「貸出中」ステータスに変更し、借用者・返却予定日などを登録するためのAPIです。

エンドポイント
~~~~~~~~~~~~~~

.. code-block:: text

   POST /api/v1/items/{item_id}/borrow

認証
~~~~

不要

リクエストヘッダー
^^^^^^^^^^^^^^^^^^

なし

パスパラメータ
~~~~~~~~~~~~~~

* ``item_id`` (integer): 対象物品のID

借用者の特定方法
~~~~~~~~~~~~~~~~

リクエストボディの ``username`` フィールドで指定します。

リクエストボディ
~~~~~~~~~~~~~~~~

JSON形式で以下のデータを送信します。

* ``username`` (string, **必須**): 借用するユーザーのユーザー名 (ログインID)
* ``due_date`` (string, **必須**): 返却予定日 (YYYY-MM-DD形式)
* ``lending_reason`` (string, optional): 貸出理由
* ``lending_location`` (string, optional): 貸出場所

.. code-block:: json

   {
     "username": "kato",
     "due_date": "2026-01-10",
     "lending_reason": "リモートワークのため",
     "lending_location": "自宅"
   }

レスポンス
~~~~~~~~~~

成功時 (HTTP 200 OK):

更新された物品情報が返されます。

.. code-block:: json

   {
       "name": "Note PC B",
       "management_code": "PC-002",
       "status": "borrowed",
       "owner_id": 1,
       "due_date": "2026-01-10",
       "lending_reason": "リモートワークのため",
       "lending_location": "自宅",
       "id": 2,
       ...
   }

エラー
~~~~~~

* **400 Bad Request**: ``due_date`` が不足している場合、または対象物品が既に貸出中の場合など。
* **401 Unauthorized**: 認証トークンが無効または不足している場合。
* **404 Not Found**: 指定された ``item_id`` の物品が存在しない場合。


物品の返却登録
--------------

物品を「利用可能」ステータスに戻すためのAPIです。

エンドポイント
~~~~~~~~~~~~~~

.. code-block:: text

   POST /api/v1/items/{item_id}/return

認証
~~~~

不要

リクエストヘッダー
^^^^^^^^^^^^^^^^^^

なし

パスパラメータ
~~~~~~~~~~~~~~

* ``item_id`` (integer): 対象物品のID

リクエストボディ
~~~~~~~~~~~~~~~~

なし

レスポンス
~~~~~~~~~~

成功時 (HTTP 200 OK):

更新された物品情報が返されます。

.. code-block:: json

   {
       "name": "Note PC B",
       "management_code": "PC-002",
       "status": "available",
       "owner_id": null,
       "due_date": null,
       ...
   }

エラー
~~~~~~

* **400 Bad Request**: 対象物品が「貸出中」ではない場合。
* **404 Not Found**: 指定された ``item_id`` の物品が存在しない場合。

Pythonによる利用例
------------------

APIを利用して操作を行うPythonスクリプトのサンプルです。
用途に合わせて3つのファイルに分けています。

1. 物品ステータス一覧の取得 (``sample_get_status.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   :caption: sample_get_status.py
   :linenos:

   import requests
   import json

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
           for item in items:
               status = item['status']
               name = item['name']
               owner = item.get('owner_name') or "なし"
               print(f"物品名: {name: <15} | ステータス: {status: <10} | 借用者: {owner}")
               
       except requests.exceptions.RequestException as e:
           print(f"エラーが発生しました: {e}")

   if __name__ == "__main__":
       get_items_status()


2. 物品の貸出 (``sample_borrow.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   :caption: sample_borrow.py
   :linenos:

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
       # 仮のIDとユーザー名で実行
       TARGET_ITEM_ID = 2
       USERNAME = "admin" 
       
       # 返却日 (1週間後)
       due_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
       
       print(f"--- 貸出処理開始 (Item ID: {TARGET_ITEM_ID}) ---")
       borrow_item(TARGET_ITEM_ID, USERNAME, due_date, "プロジェクト利用のため")

3. 物品の返却 (``sample_return.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   :caption: sample_return.py
   :linenos:

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
       # 仮のIDで実行
       TARGET_ITEM_ID = 2
       
       print(f"--- 返却処理開始 (Item ID: {TARGET_ITEM_ID}) ---")
       return_item(TARGET_ITEM_ID)
