
import csv
import json
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 프로젝트 파일 경로
PROJECT_DIR = Path(__file__).resolve().parent
TEST_FILE = PROJECT_DIR / "trafficnews_test.jsonl"
TRAIN_FILE = PROJECT_DIR / "trafficnews_train.jsonl"
VALID_FILE = PROJECT_DIR / "trafficnews_validation.jsonl"
OUTPUT_FILE = PROJECT_DIR / "trafficnews_model_comparison.csv"

GRAPH_FILES = [
    PROJECT_DIR / "trafficnews_loss.png",
    PROJECT_DIR / "trafficnews_data_split.png",
    PROJECT_DIR / "trafficnews_lead_length.png",
]

# 기존 결과는 덮어쓰지 않음
for file_path in [OUTPUT_FILE, *GRAPH_FILES]:
    if file_path.exists():
        raise FileExistsError(f"Output already exists: {file_path}")

def read_jsonl(file_path):
    with file_path.open("r", encoding="utf-8-sig") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]

train_data = read_jsonl(TRAIN_FILE)
valid_data = read_jsonl(VALID_FILE)
test_data = read_jsonl(TEST_FILE)

print("Train:", len(train_data))
print("Validation:", len(valid_data))
print("Test:", len(test_data))

assert (len(train_data), len(valid_data), len(test_data)) == (82, 10, 10)

# Ollama 모델에 동일한 조건으로 요청
def generate_lead(model_name, instruction, source):
    prompt = (
        f"{instruction}\n\n"
        f"{source}\n\n"
        "Write only one Korean news lead sentence."
    )

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 3407,
            "num_ctx": 2048,
            "num_predict": 140,
        },
    }

    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=240) as response:
        result = json.load(response)

    return result.get("response", "").strip()


# 1. 기본 모델과 파인튜닝 모델 비교
results = []

for index, row in enumerate(test_data, start=1):
    print(f"Comparing {index}/10", flush=True)

    instruction = row["instruction"]
    source = row["input"]

    base_output = generate_lead("qwen2.5:3b", instruction, source)
    tuned_output = generate_lead("trafficnews", instruction, source)

    if not base_output or not tuned_output:
        raise ValueError(f"Empty model response at sample {index}")

    results.append({
        "sample_id": index,
        "source": source,
        "reference_lead": row["output"],
        "base_model": base_output,
        "fine_tuned_model": tuned_output,
        "base_review": "pending",
        "fine_tuned_review": "pending",
    })

with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)

print("Comparison CSV saved:", OUTPUT_FILE.name)

# 2. 학습 Loss 선그래프
# 실제 2026-11-17 학습 로그에서 확인한 값
steps = [5, 10, 15, 20]
losses = [1.954, 1.749, 1.647, 1.581]

plt.figure(figsize=(8, 5))
plt.plot(steps, losses, marker="o")
plt.title("Trafficnews - Training Loss")
plt.xlabel("Training Step")
plt.ylabel("Loss")
plt.xticks(steps)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAPH_FILES[0], dpi=160)
plt.close()

# 3. 데이터 분할 막대그래프
labels = ["Train", "Validation", "Test"]
counts = [len(train_data), len(valid_data), len(test_data)]

plt.figure(figsize=(8, 5))
bars = plt.bar(labels, counts)

for bar, count in zip(bars, counts):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        count + 1,
        str(count),
        ha="center",
    )

plt.title("Trafficnews - Dataset Split")
plt.ylabel("Number of Samples")
plt.ylim(0, max(counts) * 1.15)
plt.tight_layout()
plt.savefig(GRAPH_FILES[1], dpi=160)
plt.close()

# 4. 정답 리드 길이 히스토그램
all_data = train_data + valid_data + test_data
lead_lengths = [len(str(row["output"])) for row in all_data]

plt.figure(figsize=(8, 5))
plt.hist(lead_lengths, bins=12, edgecolor="black")
plt.title("Trafficnews - Reference Lead Length")
plt.xlabel("Characters")
plt.ylabel("Number of Leads")
plt.tight_layout()
plt.savefig(GRAPH_FILES[2], dpi=160)
plt.close()

print("Graphs saved:")
for graph_file in GRAPH_FILES:
    print("-", graph_file.name)

print("Evaluation outputs: OK")
