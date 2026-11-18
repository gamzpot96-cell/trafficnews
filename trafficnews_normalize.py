
from pathlib import Path
import re
import pandas as pd

# 입력 및 출력 파일
input_file = Path("trafficnews_cleaned.csv")
output_file = Path("trafficnews_normalized.csv")

df = pd.read_csv(input_file)

def normalize_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # 줄바꿈 앞뒤 공백 제거
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)

    # 본문의 줄바꿈을 공백으로 변경
    text = text.replace("\n", " ")

    # 여러 공백을 하나로 정리
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# 본문 정규화
df["본문"] = df["본문"].apply(normalize_text)

# 새 파일에 저장
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("줄바꿈 정리 완료!")
print("데이터 수:", len(df))
print("본문 글자 수:", len(df.loc[0, "본문"]))
print("줄바꿈 개수:", df.loc[0, "본문"].count("\n"))

print("\n===== 정규화된 본문 =====")
print(df.loc[0, "본문"])
