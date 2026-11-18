
from pathlib import Path
import pymupdf

# PDF 파일 경로
pdf_path = Path("trafficnews_sample.pdf")

if not pdf_path.exists():
    print("PDF 파일을 찾을 수 없습니다.")
else:
    # PDF 열기
    with pymupdf.open(pdf_path) as document:
        print("PDF 페이지 수:", len(document))

        # 페이지별 텍스트 추출
        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")

            print(f"\n===== {page_number}페이지 =====")
            print(page_text)

import pandas as pd

# PDF 전체 텍스트 추출
with pymupdf.open(pdf_path) as document:
    full_text = "\n".join(
        page.get_text("text") for page in document
    )

# 기존 크롤링 CSV 읽기
csv_path = Path("trafficnews_crawling.csv")
df = pd.read_csv(csv_path)

# 본문 열 추가
df["본문"] = full_text

# 기존 CSV에 저장
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("\nCSV 본문 추가 완료!")
print("데이터 수:", len(df))
print("본문 글자 수:", len(full_text))
print("CSV 열:", df.columns.tolist())
