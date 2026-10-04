from pathlib import Path

from app.evaluation.benchmark import load_dataset, run_benchmark

ROOT = Path(__file__).parents[2]


def test_versioned_banking_dataset_has_stable_unique_cases() -> None:
    dataset = load_dataset(ROOT / "evaluation/datasets/banking-rag-v1.jsonl")

    assert len(dataset) == 8
    assert len({case.id for case in dataset}) == len(dataset)
    assert all(case.expected_source.endswith(".md") for case in dataset)


def test_offline_corpus_benchmark_meets_baseline_thresholds() -> None:
    report = run_benchmark(
        ROOT / "evaluation/datasets/banking-rag-v1.jsonl",
        ROOT / "data/sample/banking",
    )

    assert report.recall_at_3 >= 0.875
    assert report.answer_term_coverage == 1.0

