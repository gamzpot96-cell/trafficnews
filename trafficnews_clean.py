
from pathlib import Path
import re
import pandas as pd

# 원본과 결과 파일 경로
input_file = Path("trafficnews_crawling.csv")
output_file = Path("trafficnews_cleaned.csv")

# 원본 CSV 읽기
df = pd.read_csv(input_file)

def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # 페이지 번호 제거
    text = re.sub(r"(?m)^\s*-\s*\d+\s*-\s*$", "", text)

    # 문서 마지막의 담당자 연락처 영역 제거
    footer = "\n담당부서\n대도시권광역교통위원회"

    if footer in text:
        text = text.split(footer, 1)[0]

    # 각 줄의 앞뒤 공백 제거
    lines = [line.strip() for line in text.splitlines()]

    # 빈 줄 제거
    lines = [line for line in lines if line]

    return "\n".join(lines)

# 본문 정제
df["본문"] = df["본문"].apply(clean_text)

# 새 CSV로 저장
df.to_csv(output_file, index=False, encoding="utf-8-sig")

# 결과 확인
print("정제 완료!")
print("데이터 수:", len(df))
print("정제된 본문 글자 수:", len(df.loc[0, "본문"]))
print("담당자 연락처 포함 여부:",
      bool(re.search(r"044-\d{3}-\d{4}", df.loc[0, "본문"])))

print("\n===== 정제된 본문 =====")
print(df.loc[0, "본문"])
