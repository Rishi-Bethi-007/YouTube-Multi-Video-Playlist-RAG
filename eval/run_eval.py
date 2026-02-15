import json
from pathlib import Path
import pandas as pd

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

from src.retrieve import answer_question
from src.config import NAMESPACE

TESTSET_PATH = Path("data/eval/testset.json")

def main():
    tests = json.loads(TESTSET_PATH.read_text(encoding="utf-8"))

    rows = []
    for t in tests:
        q = t["question"]
        gt = t.get("ground_truth", "")
        out = answer_question(q, namespace=NAMESPACE)

        # RAGAS expects "contexts" as list[str]. We can reconstruct from sources + internal behavior:
        # We'll store the prompt contexts implicitly by using sources URLs + answer;
        # For now we approximate contexts by listing the source links as context strings.
        contexts = [f"{s['video_id']}@{s['start']} {s['url']}" for s in out["sources"]]

        rows.append({
            "question": q,
            "answer": out["answer"],
            "contexts": contexts,
            "ground_truth": gt,
            "total_ms": out["timings"].get("total_ms", None),
            "rewrite_ms": out["timings"].get("rewrite_ms", None),
            "embed_query_ms": out["timings"].get("embed_query_ms", None),
            "retrieve_ms": out["timings"].get("retrieve_ms", None),
            "db_fetch_ms": out["timings"].get("db_fetch_ms", None),
            "rerank_ms": out["timings"].get("rerank_ms", None),
            "generate_ms": out["timings"].get("generate_ms", None),
        })

    df = pd.DataFrame(rows)
    print("\n=== Latency summary (ms) ===")
    print(df[["total_ms","rewrite_ms","embed_query_ms","retrieve_ms","db_fetch_ms","rerank_ms","generate_ms"]].describe())

    # Build dataset for RAGAS
    ds = Dataset.from_dict({
        "question": df["question"].tolist(),
        "answer": df["answer"].tolist(),
        "contexts": df["contexts"].tolist(),
        "ground_truth": df["ground_truth"].tolist(),
    })

    # Minimal metrics to start (you can add more later)
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy])
    print("\n=== RAGAS ===")
    print(result)

if __name__ == "__main__":
    main()
