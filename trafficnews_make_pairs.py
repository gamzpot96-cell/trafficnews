
from pathlib import Path
import pandas as pd

# 정제된 보도자료 불러오기
input_file = Path("trafficnews_final.csv")
output_file = Path("trafficnews_pairs_checked.csv")

df = pd.read_csv(input_file)

# 사람이 검수한 기사 첫 문장
lead = (
    "국토교통부 대도시권광역교통위원회가 2026년 11월 11일 "
    "관계기관 합동 TF 회의를 열어 신도시 교통대책에 포함된 "
    "도로사업 16곳의 추진 상황과 인허가 지연 요인을 "
    "점검할 계획이라고 밝혔다."
)

# 입력 본문과 정답 문장을 한 쌍으로 구성
pair = {
    "본문": df.loc[0, "본문"],
    "리드": lead,
    "판정": "사용",
    "메모": "원본 PDF와 핵심 내용 대조",
    "원본URL": df.loc[0, "원본URL"],
}

# 기존 학습 데이터를 실수로 덮어쓰지 않도록 확인
if output_file.exists():
    print("이미 학습 데이터 파일이 존재합니다. 덮어쓰지 않았습니다.")
else:
    pairs_df = pd.DataFrame([pair])
    pairs_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("학습 데이터 저장 완료!")
    print("학습 데이터 쌍:", len(pairs_df))
    print("본문 글자 수:", len(pair["본문"]))
    print("리드 글자 수:", len(pair["리드"]))
    print("검수 판정:", pair["판정"])
    print("저장 파일:", output_file)
