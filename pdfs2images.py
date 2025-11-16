#!/usr/bin/env python3
from pathlib import Path
from pdf2image import convert_from_path


def main() -> None:
    pdf_dir = Path("pdfs")
    images_root = Path("images")

    if not pdf_dir.exists():
        raise SystemExit(f"入力ディレクトリがありません: {pdf_dir.resolve()}")

    images_root.mkdir(exist_ok=True)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"PDF ファイルが見つかりません: {pdf_dir.resolve()}")
        return

    for pdf_path in pdf_files:
        print(f"Processing {pdf_path.name} ...")

        output_dir = images_root / pdf_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        pages = convert_from_path(str(pdf_path), dpi=200)

        for page_number, page in enumerate(pages, start=1):
            out_path = output_dir / f"{page_number}.png"
            page.save(out_path, "PNG")

        print(f"  -> {len(pages)} pages saved to {output_dir}")


if __name__ == "__main__":
    main()
