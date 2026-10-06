from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_backend_image_packages_runtime_evaluation_dataset() -> None:
    dockerfile = (ROOT / "backend/Dockerfile").read_text()

    assert "COPY evaluation /evaluation" in dockerfile
    assert (ROOT / "evaluation/datasets/banking-rag-v1.jsonl").is_file()
