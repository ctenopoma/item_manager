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

必要 (User権限以上)

リクエストヘッダー
^^^^^^^^^^^^^^^^^^

* ``Authorization``: ``Bearer {access_token}``

パスパラメータ
~~~~~~~~~~~~~~

* ``item_id`` (integer): 対象物品のID

借用者の特定方法
~~~~~~~~~~~~~~~~

借用者は、リクエストヘッダーの ``Authorization`` トークンに紐付けられたユーザーとして自動的に特定されます。
リクエストボディでユーザーIDを指定する必要はありません。APIを実行したユーザー自身が「借用者」として登録されます。

リクエストボディ
~~~~~~~~~~~~~~~~

JSON形式で以下のデータを送信します。

* ``due_date`` (string, **必須**): 返却予定日 (YYYY-MM-DD形式)
* ``lending_reason`` (string, optional): 貸出理由
* ``lending_location`` (string, optional): 貸出場所

.. code-block:: json

   {
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

必要 (User権限以上)

.. note::
   **権限について**
   
   * **一般ユーザー**: 自分が借りている物品のみ返却できます。他人の物品を返そうとすると ``403 Forbidden`` になります。
   * **管理者 (Admin)**: 誰が借りているかに関わらず、強制的に返却処理を行えます。

リクエストヘッダー
^^^^^^^^^^^^^^^^^^

* ``Authorization``: ``Bearer {access_token}``

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
* **403 Forbidden**: 自分が借用者ではなく、かつ管理者でもない場合。
* **404 Not Found**: 指定された ``item_id`` の物品が存在しない場合。