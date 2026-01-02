ユーザーと物品の追加方法
================================

ユーザーと物品を追加するには、主に3つの方法があります。

1. **管理画面 (Admin GUI) を使用する方法** (推奨)
2. **API (Swagger UI) を使用する方法**
3. **スクリプトを使用する方法** (データ初期化)

1. 管理画面 (Admin GUI) を使用する方法
-----------------------------------------

Djangoの管理画面のようなGUIでデータを操作できます。

手順
^^^^^^

1. **管理画面にアクセス**
   ブラウザで http://127.0.0.1:8000/admin を開きます。

2. **データの追加**
   - 画面上部のメニュー、またはダッシュボードから **Users** や **Items** を選択します。
   - 右上の **New** ボタンをクリックします。
   - 必要な情報を入力して **Save** をクリックします。

3. **データの編集・削除**
   - リストから対象の行を探し、右側の編集アイコン（鉛筆）や削除アイコン（ゴミ箱）をクリックします。

2. API (Swagger UI) を使用する方法
-----------------------------------------

サーバーが起動している状態で、ブラウザからAPI経由でデータを追加できます。

手順
^^^^^^

1. **Swagger UI にアクセス**
   ブラウザで http://127.0.0.1:8000/docs を開きます。

2. **管理者としてログイン (Authorize)**
   データの追加には管理者権限が必要です。

   - 右上の **Authorize** ボタンをクリックします。
   - 以下の認証情報を入力します（ ``seed_db.py`` の初期設定）。

     - **Username**: ``admin``
     - **Password**: ``adminpassword``

   - **Authorize** → **Close** をクリックします。

3. **ユーザーを追加する**
   - ``users`` セクションの ``POST /api/v1/users/`` を開きます。
   - **Try it out** をクリックします。
   - Request body にユーザー情報を入力します。
     
     .. code-block:: json

        {
          "username": "newuser",
          "display_name": "新規ユーザー",
          "password": "userpassword"
        }

   - **Execute** をクリックして追加します。

4. **物品を追加する**
   - ``items`` セクションの ``POST /api/v1/items/`` を開きます。
   - **Try it out** をクリックします。
   - Request body に物品情報を入力します。

     .. code-block:: json

        {
          "name": "New Item Name",
          "management_code": "CODE-001",
          "category": "PC"
        }

   - **Execute** をクリックして追加します。

3. スクリプトを使用する方法
-----------------------------------------

Pythonスクリプトを使ってデータを追加することもできます。
``seed_db.py`` はデータベースを初期化（全削除）してしまうため、**追加のみを行う別のスクリプト**を作成することをお勧めします。

``add_data.py`` の作成例
^^^^^^^^^^^^^^^^^^^^^^^^

以下の内容で ``add_data.py`` というファイルをプロジェクトルート（ ``seed_db.py`` と同じ場所）に作成し、実行してください。

.. code-block:: python

    from inventory_app import database, crud, schemas
    from inventory_app.database import SessionLocal

    def add_data():
        db = SessionLocal()
        try:
            # --- ユーザーの追加 ---
            try:
                new_user = crud.create_user(
                    db, 
                    schemas.UserCreate(
                        username="kato", 
                        password="password", 
                        display_name="加藤 浩二"
                    )
                )
                print(f"User created: {new_user.username}")
            except Exception as e:
                print(f"User creation failed (might already exist): {e}")

            # --- 物品の追加 ---
            new_item = crud.create_item(
                db, 
                schemas.ItemCreate(
                    name="iPad Air", 
                    management_code="TBL-001", 
                    category="Tablet"
                )
            )
            print(f"Item created: {new_item.name}")

        finally:
            db.close()

    if __name__ == "__main__":
        add_data()

実行方法
^^^^^^^^^^^^

.. code-block:: bash

    uv run python add_data.py
