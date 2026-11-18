
import pandas as pd

# 원본과 정규화 데이터 읽기
original = pd.read_csv("trafficnews_crawling.csv")
normalized = pd.read_csv("trafficnews_normalized.csv")

original_text = str(original.loc[0, "본문"])
normalized_text = str(normalized.loc[0, "본문"])

# 확인할 주요 표현
check_items = [
    "16개 도로사업",
    "11월 11일",
    "10월 26일",
    "2개 사업",
    "하남교산",
    "인천계양",
    "과천과천",
    "안산장상",
    "시흥장현",
]

print("===== 핵심 정보 검증 =====")

all_passed = True

for item in check_items:
    original_found = item in original_text
    normalized_found = item in normalized_text

    passed = original_found and normalized_found

    print(f"{item}: {'OK' if passed else '확인 필요'}")

    if not passed:
        all_passed = False

print("\n===== 최종 결과 =====")

if all_passed:
    print("핵심 표현 9개가 원본과 정규화 데이터에 모두 존재합니다.")
else:
    print("일부 표현을 확인해야 합니다.")
