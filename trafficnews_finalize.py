
from pathlib import Path
import pandas as pd

# 기존 정규화 데이터 읽기
input_file = Path("trafficnews_normalized.csv")
output_file = Path("trafficnews_final.csv")

df = pd.read_csv(input_file)

# 원본 PDF와 대조해 확인한 띄어쓰기 수정
corrections = {
    "확장및 통합": "확장 및 통합",
    "인허가등": "인허가 등",
    "특히,TF": "특히, TF",
}

def correct_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    for before, after in corrections.items():
        text = text.replace(before, after)

    return text

# 본문 수정
df["본문"] = df["본문"].apply(correct_text)

# 최종 CSV 저장
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print("띄어쓰기 수정 완료!")
print("데이터 수:", len(df))
print("본문 글자 수:", len(df.loc[0, "본문"]))

print("\n===== 수정 결과 확인 =====")
for corrected in corrections.values():
    print(f"{corrected}: {'OK' if corrected in df.loc[0, '본문'] else '확인 필요'}")

print("\n저장 파일:", output_file)
