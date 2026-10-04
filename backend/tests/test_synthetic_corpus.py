import json
import re
from pathlib import Path

CORPUS = Path(__file__).parents[2] / "data/sample/banking"


def parse_frontmatter(content: str) -> dict[str, str]:
    assert content.startswith("---\n")
    header = content.split("---\n", 2)[1]
    return dict(line.split(":", 1) for line in header.splitlines() if ":" in line)


def test_corpus_is_explicitly_synthetic_and_covers_demo_domains() -> None:
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    categories = {item["category"] for item in manifest["documents"]}

    assert manifest["synthetic"] is True
    assert len(manifest["documents"]) >= 8
    assert {
        "savings",
        "kyc_aml",
        "personal_loans",
        "credit_cards",
        "mortgages",
        "transactions_fraud",
        "fees_rates",
        "branch_support",
    } <= categories

    for item in manifest["documents"]:
        content = (CORPUS / item["file"]).read_text(encoding="utf-8")
        metadata = parse_frontmatter(content)
        assert metadata["synthetic"].strip() == "true"
        assert metadata["version"].strip() == item["version"]
        assert "fictional" in content.lower() or "synthetic" in content.lower()


def test_corpus_contains_facts_for_primary_demo_questions() -> None:
    corpus_text = re.sub(
        r"\s+",
        " ",
        "\n".join(path.read_text(encoding="utf-8") for path in CORPUS.glob("*.md")),
    ).lower()

    for expected in (
        "average monthly balance of inr 25,000",
        "government-issued photo identity",
        "self-employed customer may apply",
        "1.5 percent of the sanctioned amount",
        "gold credit card",
        "outgoing transfers",
    ):
        assert expected in corpus_text
