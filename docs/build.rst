ビルド・実行方法
================

本プロジェクトのビルドおよび実行方法について説明します。

前提条件
--------

以下のツールがインストールされていることを確認してください。

*   **Python 3.12+**
*   **uv** (Pythonパッケージ管理ツール): `curl -LsSf https://astral.sh/uv/install.sh | sh`
*   **Docker** & **Docker Compose** (コンテナ実行用)

ローカル環境での実行 (開発用)
-----------------------------

`uv` を使用して依存関係を解決し、ローカルでサーバーを起動します。

セットアップ
~~~~~~~~~~~~

プロジェクトのルートディレクトリで以下のコマンドを実行し、仮想環境を作成・同期します。

.. code-block:: bash

   uv sync

APIサーバーの起動
~~~~~~~~~~~~~~~~~

以下のコマンドで開発用サーバー (Hot Reload有効) を起動します。

.. code-block:: bash

   uv run uvicorn inventory_app.main:app --reload

サーバー起動後、ブラウザで `http://localhost:8000/docs` にアクセスすると、Swagger UI が表示されます。

Docker環境での実行
------------------

Dockerを使用してアプリケーションをコンテナ化して実行します。

ビルド
~~~~~~

.. code-block:: bash

   docker-compose build

起動
~~~~

.. code-block:: bash

   docker-compose up

バックグラウンドで実行する場合は `-d` オプションを付けてください。

.. code-block:: bash

   docker-compose up -d

ドキュメントのビルド (Sphinx)
-----------------------------

本ドキュメント (Sphinx) を HTML 形式でビルドするには、以下のコマンドを実行します。

.. code-block:: bash

   cd docs
   uv run sphinx-build -M html . _build

ビルドが成功すると、 `docs/_build/html/index.html` が生成されます。
