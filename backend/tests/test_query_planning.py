from app.generation.query import QueryIntent, RuleBasedQueryPlanner


def test_planner_classifies_comparison_and_expands_banking_abbreviations() -> None:
    plan = RuleBasedQueryPlanner().plan(" Compare KYC requirements versus AML review ")

    assert plan.intent == QueryIntent.COMPARISON
    assert plan.route == "hybrid_knowledge"
    assert "know your customer KYC" in plan.retrieval_query
    assert "anti money laundering AML" in plan.retrieval_query
    assert set(plan.transformations) == {"expanded:kyc", "expanded:aml"}


def test_planner_marks_latest_policy_queries_without_losing_original_text() -> None:
    plan = RuleBasedQueryPlanner().plan("According to the latest policy, what happens?")

    assert plan.intent == QueryIntent.LATEST_POLICY
    assert plan.original_query == "According to the latest policy, what happens?"

