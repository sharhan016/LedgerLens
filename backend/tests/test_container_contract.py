from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_backend_image_packages_runtime_evaluation_dataset() -> None:
    dockerfile = (ROOT / "backend/Dockerfile").read_text()
    dockerignore = (ROOT / ".dockerignore").read_text().splitlines()

    assert "COPY evaluation /evaluation" in dockerfile
    assert "evaluation" not in dockerignore
    assert (ROOT / "evaluation/datasets/banking-rag-v1.jsonl").is_file()
