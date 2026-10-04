import json
import urllib.request


API = "http://127.0.0.1:8000"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def request(path: str, *, token: str | None = None, payload: dict | None = None) -> object:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode() if payload is not None else None
    method = "POST" if payload is not None else "GET"
    with OPENER.open(
        urllib.request.Request(API + path, data=body, headers=headers, method=method),
        timeout=30,
    ) as response:
        return json.load(response)


ready = request("/health/ready")
login = request("/api/v1/auth/demo-login", payload={"persona": "compliance"})
assert isinstance(login, dict)
token = str(login["access_token"])
documents = request("/api/v1/documents", token=token)
answer = request(
    "/api/v1/assistant/ask",
    token=token,
    payload={"question": "What is the minimum balance for the Premium Savings Account?"},
)
assert isinstance(ready, dict) and ready["status"] == "ok"
assert isinstance(documents, list) and len(documents) == 8
assert isinstance(answer, dict)
assert answer["model"] == "demo-extractive-not-llm"
assert "INR 25,000" in answer["answer"]
assert answer["citations"]
assert answer["grounding"]["grounded"] is True
print(
    json.dumps(
        {
            "readiness": ready["status"],
            "documents": len(documents),
            "model": answer["model"],
            "citation": answer["citations"][0]["source"],
            "grounded": answer["grounding"]["grounded"],
        },
        indent=2,
    )
)
