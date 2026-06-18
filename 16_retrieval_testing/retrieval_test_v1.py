#!/usr/bin/env python3
"""Run retrieval tests against the Azure AI Search V4 RAG index."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
TEST_CASES_PATH = Path(__file__).resolve().with_name("retrieval_test_cases.json")
RESULTS_PATH = Path(__file__).resolve().with_name("retrieval_test_results.json")
REPORT_PATH = Path(__file__).resolve().with_name("retrieval_test_report.md")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def required(env: dict[str, str], key: str) -> str:
    value = env.get(key) or os.environ.get(key)
    if not value:
        raise ValueError(f"Missing required environment value: {key}")
    return value


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def request_json(method: str, url: str, headers: dict[str, str], payload: Any | None = None, timeout: int = 180) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1000]}") from exc


def endpoint_url(endpoint: str, path: str, api_version: str) -> str:
    return f"{endpoint.rstrip('/')}{path}?api-version={urllib.parse.quote(api_version)}"


def embedding_url(endpoint: str, deployment: str, api_version: str) -> str:
    return f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/embeddings?api-version={urllib.parse.quote(api_version)}"


def embed_query(env: dict[str, str], text: str) -> list[float]:
    url = embedding_url(required(env, "AZURE_OPENAI_ENDPOINT"), required(env, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"), required(env, "AZURE_OPENAI_API_VERSION"))
    headers = {"Content-Type": "application/json", "api-key": required(env, "AZURE_OPENAI_API_KEY")}
    _, body = request_json("POST", url, headers, {"input": [text]})
    return body["data"][0]["embedding"]


def search(env: dict[str, str], query: str, mode: str, top: int, vector: list[float] | None, filter_expr: str | None) -> dict[str, Any]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    url = endpoint_url(endpoint, f"/indexes/{index_name}/docs/search", api_version)
    headers = {"Content-Type": "application/json", "api-key": required(env, "AZURE_SEARCH_API_KEY")}
    body: dict[str, Any] = {
        "top": top,
        "select": "id,page_id,section_id,title,source_url,content,chunk_index,chunk_total,related_page_ids",
        "count": True,
    }
    if filter_expr:
        body["filter"] = filter_expr
    if mode == "keyword":
        body["search"] = query
    elif mode == "vector":
        body["search"] = "*"
        body["vectorQueries"] = [{"kind": "vector", "vector": vector, "fields": "content_vector", "k": top}]
    elif mode == "hybrid":
        body["search"] = query
        body["vectorQueries"] = [{"kind": "vector", "vector": vector, "fields": "content_vector", "k": top}]
    else:
        raise ValueError(f"Unknown mode: {mode}")
    _, result = request_json("POST", url, headers, body)
    return result


def compact_result(raw: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for item in raw.get("value", []):
        content = item.get("content", "")
        rows.append({
            "score": item.get("@search.score"),
            "page_id": item.get("page_id"),
            "section_id": item.get("section_id"),
            "title": item.get("title"),
            "source_url": item.get("source_url"),
            "chunk_index": item.get("chunk_index"),
            "chunk_total": item.get("chunk_total"),
            "snippet": content[:350].replace("\n", " "),
        })
    return {"count": raw.get("@odata.count"), "results": rows}


def evaluate(test: dict[str, Any], compact: dict[str, Any]) -> dict[str, Any]:
    page_ids = [r["page_id"] or "" for r in compact["results"]]
    joined = "\n".join([json.dumps(r, ensure_ascii=False) for r in compact["results"]]).lower()
    checks: dict[str, Any] = {}
    if test.get("expected_page_ids"):
        expected = set(test["expected_page_ids"])
        checks["expected_page_id_hit"] = bool(expected.intersection(page_ids))
    if test.get("expected_page_id_contains"):
        checks["expected_page_id_contains_hit"] = any(any(token in pid for token in test["expected_page_id_contains"]) for pid in page_ids)
    if test.get("expected_page_id_startswith"):
        checks["expected_page_id_startswith_hit"] = all(any(pid.startswith(prefix) for prefix in test["expected_page_id_startswith"]) for pid in page_ids[:3]) if page_ids else False
    if test.get("expected_signals"):
        hits = [signal for signal in test["expected_signals"] if signal.lower() in joined]
        checks["expected_signal_hits"] = hits
        checks["expected_signal_hit_count"] = len(hits)
    checks["top_page_ids"] = page_ids[:5]
    return checks


def write_report(payload: dict[str, Any]) -> None:
    lines = [
        "# Retrieval Test Report\n",
        f"Generated at: {payload['generated_at']}\n\n",
        "## Summary\n",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"- {key}: {value}\n")
    for category in ["sensitivity_test", "specificity_test", "filter_test"]:
        lines.append(f"\n## {category}\n")
        for test in [t for t in payload["tests"] if t["category"] == category]:
            lines.append(f"\n### {test['id']}\n")
            lines.append(f"Question: {test['question']}\n\n")
            for mode in test["modes"]:
                top_ids = ", ".join(mode["evaluation"].get("top_page_ids", [])[:3])
                lines.append(f"- {mode['mode']}: top pages: {top_ids}\n")
                if mode["results"]:
                    first = mode["results"][0]
                    lines.append(f"  first: {first['page_id']} | {first['title']} | score={first['score']}\n")
    REPORT_PATH.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run keyword/vector/hybrid retrieval tests.")
    parser.add_argument("--top", type=int, default=0, help="Override test top_k.")
    parser.add_argument("--modes", default="keyword,vector,hybrid")
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    cases = json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    top = args.top or int(cases.get("top_k", 5))
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]
    test_outputs = []
    failures = []
    started = now_iso()

    for test in cases["tests"]:
        vector = None
        if any(mode in {"vector", "hybrid"} for mode in modes):
            vector = embed_query(env, test["question"])
        test_record = {k: v for k, v in test.items() if k != "expected_signals"}
        test_record["modes"] = []
        for mode in modes:
            try:
                raw = search(env, test["question"], mode, top, vector, test.get("filter"))
                compact = compact_result(raw)
                evaluation = evaluate(test, compact)
                test_record["modes"].append({"mode": mode, "count": compact["count"], "results": compact["results"], "evaluation": evaluation})
            except Exception as exc:
                failures.append({"test_id": test["id"], "mode": mode, "error": str(exc)})
        test_outputs.append(test_record)
        time.sleep(0.2)

    summary = {
        "tests": len(cases["tests"]),
        "modes_per_test": len(modes),
        "search_calls_expected": len(cases["tests"]) * len(modes),
        "failures": len(failures),
        "categories": sorted({t["category"] for t in cases["tests"]}),
    }
    payload = {"generated_at": now_iso(), "started_at": started, "summary": summary, "failures": failures, "tests": test_outputs}
    RESULTS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(payload)
    print(json.dumps({"summary": summary, "failures": failures, "outputs": {"results": str(RESULTS_PATH), "report": str(REPORT_PATH)}}, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
