from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from app.evaluation.benchmark import run_benchmark
from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])
ROOT = Path(__file__).parents[3]


@router.get("/summary")
async def evaluation_summary(
    principal: Annotated[Principal, Depends(require_permission(Permission.AUDIT_READ))],
) -> dict[str, object]:
    report = run_benchmark(
        ROOT / "evaluation/datasets/banking-rag-v1.jsonl",
        ROOT / "data/sample/banking",
    )
    return {
        "dataset": report.dataset,
        "cases": report.cases,
        "recall_at_3": report.recall_at_3,
        "answer_term_coverage": report.answer_term_coverage,
        "status": "passing" if report.recall_at_3 >= 0.875 else "needs_attention",
        "per_case": list(report.per_case),
    }

