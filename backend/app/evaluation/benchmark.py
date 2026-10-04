import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    id: str
    question: str
    expected_source: str
    expected_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    dataset: str
    cases: int
    recall_at_3: float
    answer_term_coverage: float
    per_case: tuple[dict[str, object], ...]


def tokens(value: str) -> set[str]:
    values = {token.lower() for token in re.findall(r"[a-z0-9]+", value) if len(token) > 2}
    return values | {token[:-1] for token in values if token.endswith("s") and len(token) > 4}


def load_dataset(path: Path) -> list[EvaluationCase]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            cases.append(
                EvaluationCase(
                    id=item["id"],
                    question=item["question"],
                    expected_source=item["expected_source"],
                    expected_terms=tuple(item["expected_terms"]),
                )
            )
    return cases


def rank_documents(question: str, corpus: Path) -> list[tuple[str, str, float]]:
    query_tokens = tokens(question)
    documents = [
        (path.name, path.read_text(encoding="utf-8")) for path in sorted(corpus.glob("*.md"))
    ]
    document_frequency = {
        token: sum(token in tokens(content) for _, content in documents) for token in query_tokens
    }
    ranked = []
    for name, content in documents:
        content_tokens = tokens(content)
        title_tokens = tokens(name.replace("-", " ").removesuffix(".md"))
        score = sum(
            math.log((len(documents) + 1) / (document_frequency[token] + 1)) + 1
            for token in query_tokens & content_tokens
        )
        score += 1.5 * len(query_tokens & title_tokens)
        ranked.append((name, content, score))
    return sorted(ranked, key=lambda item: (item[2], item[0]), reverse=True)


def run_benchmark(dataset: Path, corpus: Path) -> EvaluationReport:
    cases = load_dataset(dataset)
    results: list[dict[str, object]] = []
    recalls = 0
    term_scores = []
    for case in cases:
        ranked = rank_documents(case.question, corpus)
        top_sources = [name for name, _, _ in ranked[:3]]
        recalls += int(case.expected_source in top_sources)
        expected_document = next(content for name, content, _ in ranked if name == case.expected_source)
        content_lower = re.sub(r"\s+", " ", expected_document.lower())
        covered = sum(
            re.sub(r"\s+", " ", term.lower()) in content_lower for term in case.expected_terms
        )
        term_coverage = covered / (len(case.expected_terms) or 1)
        term_scores.append(term_coverage)
        results.append(
            {
                "id": case.id,
                "expected_source": case.expected_source,
                "top_3": top_sources,
                "retrieved": case.expected_source in top_sources,
                "answer_term_coverage": round(term_coverage, 4),
            }
        )
    denominator = len(cases) or 1
    return EvaluationReport(
        dataset=dataset.name,
        cases=len(cases),
        recall_at_3=round(recalls / denominator, 4),
        answer_term_coverage=round(sum(term_scores) / denominator, 4),
        per_case=tuple(results),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the deterministic LedgerLens corpus benchmark")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_benchmark(args.dataset, args.corpus)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(asdict(report), indent=2) + "\n", encoding="utf-8")
    print(
        f"evaluation cases={report.cases} recall@3={report.recall_at_3:.3f} "
        f"term_coverage={report.answer_term_coverage:.3f}"
    )
    if report.recall_at_3 < 0.875 or report.answer_term_coverage < 0.95:
        raise SystemExit("evaluation thresholds not met")


if __name__ == "__main__":
    main()
