# pdf2image2rag

図解や画像の多い PDF 媒体資料を、AI（GPT-5）を使って **RAG 用テキスト**に変換するためのバッチツールです。

- PDF → ページごとの画像（PNG）に変換
- 画像 1枚ずつを GPT-5 に投げて、RAG しやすいテキストに変換
- 1つの PDF につき 1つの `.txt` に集約

---

## スクリプト概要

### pdfs2images.py

* `pdfs/` 以下の PDF を一括で画像化し、`images/` 以下に保存する。

### images2rags.py

* PDF から変換済みのページ画像を GPT-5 に渡し、RAG 用テキストにして `rags/*.txt` に出力する。

---

## セットアップ

### 1. Python 3.10+ をインストール

#### 仮想環境
```bash
python -m venv .venv
source .venv/bin/activate  # Windows は .venv\Scripts\activate
```

### 2. ライブラリインストール

```bash
pip install pdf2image openai
```

### 3. Poppler インストール

* macOS (Homebrew):

  ```bash
  brew install poppler
  ```
  
### 4. 環境変数 `OPENAI_API_KEY` を設定

```bash
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
````

---

## 使い方

### 1. PDF を配置

`pdfs/` ディレクトリ直下に、変換したい PDF ファイルを配置します。

```text
pdfs/
  FOO媒体資料_2050_01-01.pdf
  Foo媒体資料_2025_01-03.pdf
  ...
```

### 2. PDF → 画像変換

```bash
python pdfs2images.py
```

このスクリプトが行うこと:

* `images/` 配下の **全てのサブディレクトリを削除**（`.gitkeep` のようなファイルは削除しない）
* `pdfs/*.pdf` を走査し、各 PDF ごとに

  * `images/<PDFファイル名の拡張子抜き>/` ディレクトリを作成
  * 各ページを PNG (`1.png`, `2.png`, ...) に変換して保存

    * 解像度は `dpi=200`

例:

```text
pdfs/FOO媒体資料_2050_01-01.pdf
→ images/FOO媒体資料_2050_01-01/1.png
→ images/FOO媒体資料_2050_01-01/2.png
...
```

### 3. プロンプトテンプレートの準備

`prompt_images2rags.txt` に、画像をテキスト化するためのプロンプトを記述します。
（すでに用意済みの内容を使っても、必要に応じて編集してもよい）

プレースホルダ:

* `{doc_name}`: PDF のファイル名（拡張子除く）
* `{page_number}`: ページ番号（1 から）

例（抜粋）:

```text
これは媒体資料「{doc_name}」の {page_number} ページの画像です。RAG に使いやすいテキストデータに変換してください。
...
```

### 4. 画像 → RAG 用テキスト変換

```bash
python images2rags.py
```

このスクリプトが行うこと:

1. `rags/` 配下の **全ての `.txt` ファイルを削除**（毎回クリーンな状態からやり直し）

2. `images/` 配下のサブディレクトリごとに処理

   * サブディレクトリ名（例: `FOO媒体資料_2050_01-01`）を `doc_name` とみなす
   * `rags/<doc_name>.txt` を作成

3. 各サブディレクトリ内の画像 (`.png`, `.jpg`, `.jpeg`, `.webp`) をファイル名順に処理

   * ファイル名が `1.png`, `2.png` のような数値の場合は数値順にソート
   * 1枚ずつ GPT-5 に送り、テキストを生成
   * 出力を `rags/<doc_name>.txt` に追記

出力フォーマット（例）:

```text
## FOO媒体資料_2050_01-01 page 1
... ページ 1 のテキスト ...

## FOO媒体資料_2050_01-01 page 2
... ページ 2 のテキスト ...
```

---

## 注意事項

* **API 利用料金**

  * `gpt-5` + 画像 + `max_output_tokens=128000` + `reasoning={"effort": "high"}` という設定のため、
    1ページあたりのトークン消費・料金はそれなりに大きくなります。
  * 大量のページを処理する場合は、事前に `Usage / Billing` を確認してください。

* **クォータ・RateLimit**

  * クォータ不足やレート制限により `RateLimitError` が発生すると、
    現在の実装ではメッセージを出して `sys.exit(1)` で処理を終了します。

* **上書き動作**

  * `pdfs2images.py` 実行時に `images/` 配下のサブディレクトリが全削除されます。
  * `images2rags.py` 実行時に `rags/` 配下の `.txt` が全削除されます。
  * 既存の出力を残したい場合は、スクリプトを実行する前に退避しておいてください。

* **プロンプトの調整**

  * 書き起こしの厳密さ・図の説明の詳細さ・Markdown 禁止などのポリシーは
    すべて `prompt_images2rags.txt` で定義しています。
  * 変換結果のスタイルを変えたい場合は、このファイルの文言を編集してください。

---
