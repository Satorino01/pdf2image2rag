#!/usr/bin/env python3
import base64
import mimetypes
import sys
from pathlib import Path
from openai import OpenAI, RateLimitError

MODEL = "gpt-5"

IMAGES_DIR = Path("images")
RAGS_DIR = Path("rags")
PROMPT_PATH = Path("prompt_images2rags.txt")

client = OpenAI()  # OPENAI_API_KEY を環境変数に設定しておく

def load_prompt_template() -> str:
    if not PROMPT_PATH.exists():
        raise SystemExit(f"プロンプトファイルがありません: {PROMPT_PATH.resolve()}")
    return PROMPT_PATH.read_text(encoding="utf-8")

PROMPT_TEMPLATE = load_prompt_template()

def image_to_data_url(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime is None:
        mime = "image/png"
    with path.open("rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def extract_text_from_image(image_path: Path, doc_name: str, page_number: int) -> str:
    data_url = image_to_data_url(image_path)

    prompt = PROMPT_TEMPLATE.format(
        doc_name=doc_name,
        page_number=page_number,
    )

    try:
        response = client.responses.create(
            model=MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
            reasoning={"effort": "medium"}, # 実行速度が非常に遅くなるが精度不足なら "high" に変更する
            max_output_tokens=128000, # 最大値。reasoning_tokens（思考トークン）で使い切らないようにするため
        )
    except RateLimitError as e:
        print(f"{doc_name} の {page_number} で ChatGPT API へのリクエストがコケました  : ")
        print(e)
        sys.exit(1)
    return response.output_text


def image_sort_key(p: Path):
    stem = p.stem
    try:
        return int(stem)
    except ValueError:
        return stem


def main() -> None:
    if not IMAGES_DIR.exists():
        raise SystemExit(f"images ディレクトリがありません: {IMAGES_DIR.resolve()}")

    RAGS_DIR.mkdir(exist_ok=True)

    for txt_path in RAGS_DIR.glob("*.txt"):
        txt_path.unlink()

    image_subdirs = sorted(d for d in IMAGES_DIR.iterdir() if d.is_dir())
    if not image_subdirs:
        print("images 配下にディレクトリがありません。処理を終了します。")
        return

    for doc_dir in image_subdirs:
        doc_name = doc_dir.name
        rag_path = RAGS_DIR / f"{doc_name}.txt"
        rag_path.touch(exist_ok=True)

        image_files = [
            p
            for p in doc_dir.iterdir()
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        image_files = sorted(image_files, key=image_sort_key)

        if not image_files:
            print(f"{doc_dir} に画像がないためスキップします。")
            continue

        print(f"=== {doc_name} ({len(image_files)} pages) ===")

        for page_number, image_path in enumerate(image_files, start=1):
            print(f"  page {page_number}: {image_path.name} を処理中...")

            text = extract_text_from_image(image_path, doc_name, page_number)

            with rag_path.open("a", encoding="utf-8") as f:
                f.write(f"## {doc_name} page {page_number}\n")
                f.write(text.strip())
                f.write("\n\n")

    print("完了しました。")


if __name__ == "__main__":
    main()