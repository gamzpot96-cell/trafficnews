
"""
trafficnews QLoRA 파인튜닝 재현용 코드

기본 실행: 학습 데이터 및 환경 확인만 수행
학습 실행: --train 옵션을 명시한 경우에만 수행

주의:
- 실제 학습에 사용한 원본 코드가 아닌 재구성 코드입니다.
- 기존 학습 결과와 Ollama 모델을 변경하지 않습니다.
"""

import argparse
import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

TRAIN_FILE = PROJECT_DIR / "trafficnews_train.jsonl"
VALID_FILE = PROJECT_DIR / "trafficnews_validation.jsonl"

# 기존 학습 결과와 구별되는 별도 저장 경로
OUTPUT_DIR = PROJECT_DIR / "trafficnews_reproduction_outputs"
ADAPTER_DIR = PROJECT_DIR / "trafficnews_reproduction_adapter"

MODEL_NAME = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit"
MAX_SEQUENCE_LENGTH = 1024


def load_jsonl(file_path):
    """JSONL 파일을 읽고 필요한 필드를 확인합니다."""
    if not file_path.exists():
        raise FileNotFoundError(file_path)

    rows = []

    with file_path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            row = json.loads(line)

            for column in ("instruction", "input", "output"):
                if column not in row:
                    raise ValueError(
                        f"{file_path.name} line {line_number}: "
                        f"missing {column}"
                    )

                if not isinstance(row[column], str):
                    raise ValueError(
                        f"{file_path.name} line {line_number}: "
                        f"{column} must be text"
                    )

            rows.append(row)

    return rows


def format_training_text(row):
    """보도자료와 정답 리드를 학습용 텍스트로 변환합니다."""
    return (
        f"### 지시문\n{row['instruction']}\n\n"
        f"### 입력\n{row['input']}\n\n"
        f"### 정답\n{row['output']}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--train",
        action="store_true",
        help="Start a new training run explicitly",
    )
    args = parser.parse_args()

    train_rows = load_jsonl(TRAIN_FILE)
    valid_rows = load_jsonl(VALID_FILE)

    print("Training samples:", len(train_rows))
    print("Validation samples:", len(valid_rows))

    if len(train_rows) != 82 or len(valid_rows) != 10:
        raise ValueError("Unexpected dataset size")

    # 기본 실행에서는 학습하지 않습니다.
    if not args.train:
        print("Dataset check: OK")
        print("Training: NOT STARTED")
        return

    # 기존 결과나 이전 재현 결과를 덮어쓰지 않습니다.
    if OUTPUT_DIR.exists() or ADAPTER_DIR.exists():
        raise FileExistsError(
            "Reproduction output already exists. Training cancelled."
        )

    # 실제 학습을 시작하는 경우에만 무거운 라이브러리를 불러옵니다.
    import torch
    from datasets import Dataset
    from trl import SFTConfig, SFTTrainer
    from unsloth import FastLanguageModel

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required")

    train_dataset = Dataset.from_list([
        {"text": format_training_text(row)}
        for row in train_rows
    ])

    valid_dataset = Dataset.from_list([
        {"text": format_training_text(row)}
        for row in valid_rows
    ])

    # 4비트 기본 모델 불러오기
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQUENCE_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )

    # LoRA 어댑터 설정
    model = FastLanguageModel.get_peft_model(
        model,
        r=8,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=3407,
    )

    # 일부 상세 설정은 원본 기록이 없어 재현용 기본값 사용
    training_config = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_steps=2,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        optim="adamw_8bit",
        max_length=MAX_SEQUENCE_LENGTH,
        dataset_text_field="text",
        packing=False,
        report_to="none",
        seed=3407,
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=valid_dataset,
        args=training_config,
    )

    print("Training started")
    trainer.train()

    # 원본 어댑터가 아닌 별도 폴더에 저장
    model.save_pretrained(str(ADAPTER_DIR))
    tokenizer.save_pretrained(str(ADAPTER_DIR))

    print("Training completed")
    print("Adapter saved:", ADAPTER_DIR)


if __name__ == "__main__":
    main()
