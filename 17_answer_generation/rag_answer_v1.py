#!/usr/bin/env python3
"""Step 10: RAG answer generation over Azure AI Search retrieval."""

from __future__ import annotations

import argparse
import json
import os
import re
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
PROFILE_CONTEXT_PATH = ROOT / "10_working_docs" / "profile_positioning_prompt_template.md"
ANSWER_TEMPLATE_PATH = Path(__file__).resolve().with_name("answer_prompt_template.md")
RESULTS_PATH = Path(__file__).resolve().with_name("answer_test_results.json")
REPORT_PATH = Path(__file__).resolve().with_name("answer_test_report.md")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
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
    ca_bundle = os.environ.get("AZURE_OPENAI_CA_BUNDLE")
    if ca_bundle and Path(ca_bundle).exists():
        return ssl.create_default_context(cafile=ca_bundle)
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        fallback = Path("/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/certifi/cacert.pem")
        if fallback.exists():
            return ssl.create_default_context(cafile=str(fallback))
        return ssl.create_default_context()


def request_json(method: str, url: str, headers: dict[str, str], payload: Any | None = None, timeout: int = 180) -> tuple[int, Any, float]:
    start = time.perf_counter()
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}, (time.perf_counter() - start) * 1000
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw[:1200]}") from exc


def endpoint_url(endpoint: str, path: str, api_version: str) -> str:
    return f"{endpoint.rstrip('/')}{path}?api-version={urllib.parse.quote(api_version)}"


def openai_url(endpoint: str, deployment: str, route: str, api_version: str) -> str:
    return f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/{route}?api-version={urllib.parse.quote(api_version)}"


def embed_query(env: dict[str, str], question: str) -> tuple[list[float], float]:
    url = openai_url(required(env, "AZURE_OPENAI_ENDPOINT"), required(env, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"), "embeddings", required(env, "AZURE_OPENAI_API_VERSION"))
    headers = {"Content-Type": "application/json", "api-key": required(env, "AZURE_OPENAI_API_KEY")}
    _, body, latency = request_json("POST", url, headers, {"input": [question]})
    return body["data"][0]["embedding"], latency


def search_chunks(env: dict[str, str], question: str, vector: list[float], top_k: int, mode: str, filter_expr: str | None) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    url = endpoint_url(endpoint, f"/indexes/{index_name}/docs/search", api_version)
    headers = {"Content-Type": "application/json", "api-key": required(env, "AZURE_SEARCH_API_KEY")}
    body: dict[str, Any] = {
        "top": top_k,
        "select": "id,page_id,section_id,title,source_url,content,chunk_index,chunk_total,related_page_ids",
        "count": True,
    }
    if filter_expr:
        body["filter"] = filter_expr
    if mode == "keyword":
        body["search"] = question
    elif mode == "vector":
        body["search"] = "*"
        body["vectorQueries"] = [{"kind": "vector", "vector": vector, "fields": "content_vector", "k": top_k}]
    elif mode == "hybrid":
        body["search"] = question
        body["vectorQueries"] = [{"kind": "vector", "vector": vector, "fields": "content_vector", "k": top_k}]
    else:
        raise ValueError(f"Unknown search mode: {mode}")
    _, result, latency = request_json("POST", url, headers, body)
    return result.get("value", []), latency, {"request_body_without_vector": {k: v for k, v in body.items() if k != "vectorQueries"}, "count": result.get("@odata.count")}


def build_context(chunks: list[dict[str, Any]]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}]\n"
            f"page_id: {c.get('page_id')}\n"
            f"section_id: {c.get('section_id')}\n"
            f"title: {c.get('title')}\n"
            f"url: {c.get('source_url')}\n"
            f"chunk: {c.get('chunk_index')}/{c.get('chunk_total')}\n"
            f"score: {c.get('@search.score')}\n"
            f"content: {c.get('content')}\n"
        )
    return "\n---\n".join(parts)


def build_messages(question: str, chunks: list[dict[str, Any]]) -> list[dict[str, str]]:
    profile_context = PROFILE_CONTEXT_PATH.read_text(encoding="utf-8")[:12000]
    answer_template = ANSWER_TEMPLATE_PATH.read_text(encoding="utf-8")
    retrieved_context = build_context(chunks)
    system = f"{answer_template}\n\nPROFILE POSITIONING CONTEXT:\n{profile_context}"
    user = f"Question:\n{question}\n\nRetrieved Azure AI Search context:\n{retrieved_context}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_answer(env: dict[str, str], question: str, chunks: list[dict[str, Any]]) -> tuple[str, float, dict[str, Any]]:
    url = openai_url(required(env, "AZURE_OPENAI_ENDPOINT"), required(env, "AZURE_OPENAI_CHAT_DEPLOYMENT"), "chat/completions", required(env, "AZURE_OPENAI_API_VERSION"))
    headers = {"Content-Type": "application/json", "api-key": required(env, "AZURE_OPENAI_API_KEY")}
    messages = build_messages(question, chunks)
    payload = {
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 900,
    }
    _, body, latency = request_json("POST", url, headers, payload)
    answer = body["choices"][0]["message"]["content"]
    return answer, latency, {"usage": body.get("usage", {}), "prompt_preview": messages[1]["content"][:2500]}


def is_profane_or_abusive_question(question: str) -> bool:
    q = f" {question.lower()} "
    blocked_terms = [
        " fuck", " fucking", " shit", " bullshit", " bastard", " asshole", " bitch",
        " motherfucker", " dumbass", " idiot", " stupid", " bloody hell", " piss off",
        " porn", " nude", " naked", " sex", " sexual", " fucker",
        " denga", " deng", " dengu", " denguta", " dengutaa", " denkuta", " yamma deng"
    ]
    return any(term in q for term in blocked_terms)


def profanity_guardrail_answer() -> str:
    return (
        "Direct Answer:\n"
        "Please keep the conversation professional and respectful. I can help with Rajesh Arigala's business experience, education, AI/MLOps work, projects, and role fit.\n\n"
        "Context:\n"
        "RABBIT speaks on Rajesh's behalf to interested stakeholders, so the conversation should stay pleasant, relevant, and professional."
    )


def is_language_capability_question(question: str) -> bool:
    q = question.lower().strip()
    patterns = [
        "which languages do you speak", "what languages do you speak", "can you speak",
        "do you speak hindi", "do you speak telugu", "language do you speak"
    ]
    return any(pattern in q for pattern in patterns)


def language_capability_answer() -> str:
    return (
        "Direct Answer:\n"
        "I am RABBIT, a professional AI assistant for Rajesh Arigala's business-tech profile. This version is designed to respond best in English.\n\n"
        "Context:\n"
        "I can help with Rajesh's professional journey, business experience, education, AI/MLOps work, projects, and role fit. I avoid guessing personal details that are not part of the professional profile."
    )


def is_private_personal_question(question: str) -> bool:
    q = f" {question.lower()} "
    private_terms = [
        " girlfriend", " gf", " boyfriend", " wife", " husband", " married", " marriage",
        " dating", " relationship", " single", " divorce", " children", " kids", " family details",
        " personal relationship", " private life", " love life", " race", " religion", " caste",
        " sexual orientation", " orientation", " gay", " lesbian", " political", " language identity",
        " medical record", " diagnosis", " address", " home address", " personal address",
        " online", " offline", " is he online", " is rajesh online", " available now", " right now",
        " can we call", " call him now", " speak with him now", " where is he living", " where does he live",
        " current location", " live location", " personal phone", " personal email", " whatsapp"
    ]
    return any(term in q for term in private_terms)


def private_personal_guardrail_answer() -> str:
    return (
        "Direct Answer:\n"
        "I keep this conversation focused on Rajesh Arigala's professional profile. I do not discuss personal life, protected personal attributes, live availability, online/offline status, home location, or private contact context.\n\n"
        "Context:\n"
        "RABBIT speaks on Rajesh's behalf for interested stakeholders. I can help with his business experience, Mechanical Engineering background, education, AI/MLOps work, projects, role fit, and public professional webpages."
    )


def is_compensation_question(question: str) -> bool:
    q = f" {question.lower()} "
    compensation_terms = [
        " salary", " compensation", " ctc", " package", " pay ", " paid", " pays",
        " lpa", " crore", " highest", " how much should", " how much can", " worth", " worthy",
        " market standard", " offer him", " offer rajesh", " iit salary", " iim salary", " iim guys"
    ]
    return any(term in q for term in compensation_terms)


def is_external_compensation_benchmark(question: str) -> bool:
    q = question.lower()
    external_terms = [
        "iim guys", "iim graduates", "who pays highest", "highest paying", "which company pays",
        "market salary for", "average salary", "industry salary", "salary survey", "benchmark salary"
    ]
    return any(term in q for term in external_terms)


def compensation_guardrail_answer(question: str) -> str:
    if is_external_compensation_benchmark(question) and "rajesh" not in question.lower():
        return (
            "Direct Answer:\n"
            "I do not have verified live compensation benchmark data for that question, so I should not quote salary figures for IIM graduates, companies, or industries as facts.\n\n"
            "Context:\n"
            "For real compensation benchmarking, use current recruiter data, company compensation bands, geography, seniority, and role scope. RABBIT can explain Rajesh's fit and value, but it should not act like a live salary-survey database unless that data is explicitly added and sourced."
        )

    return (
        "Direct Answer:\n"
        "Rajesh's compensation should be aligned with senior market standards for the exact role being offered. I should not quote a fixed salary number because compensation depends on role scope, geography, seniority, company stage, business ownership, and technical responsibility.\n\n"
        "Context:\n"
        "A fair offer should benchmark the specific role against current market data and then adjust for Rajesh's hybrid value: business execution, entrepreneurship through RedRybbons and R-Cafe, Mechanical Engineering foundation, IIM Calcutta Marketing and Strategy, ISB Product Management, IISc Bangalore Advanced Business Analytics, and hands-on AI/MLOps project work."
    )

def clean_user_answer(answer: str) -> str:
    text = str(answer or "")
    text = re.sub(r"\s*\[Source\s+\d+(?:\s*,\s*\d+)*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\(Source:\s*[^)]+\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*\*?\(?Source:\s*[^\n)]+\)?\*?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*[-*]?\s*\[Source\s+\d+\]\([^)]*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n\s*\*?\(?Source\s+\d+(?:\s*,\s*\d+)*[^\n]*\)?\*?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"###\s*Sources[\s\S]*$", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def answer_question(question: str, mode: str = "hybrid", top_k: int = 5, filter_expr: str | None = None) -> dict[str, Any]:
    env = load_env(ENV_PATH)
    total_start = time.perf_counter()
    status = "success"
    error = None
    embedding_latency = search_latency = answer_latency = 0.0
    chunks: list[dict[str, Any]] = []
    search_debug: dict[str, Any] = {}
    llm_debug: dict[str, Any] = {}
    answer = ""
    suppress_sources = False
    try:
        if is_profane_or_abusive_question(question):
            answer = profanity_guardrail_answer()
            suppress_sources = True
        elif is_language_capability_question(question):
            answer = language_capability_answer()
            suppress_sources = True
        elif is_private_personal_question(question):
            answer = private_personal_guardrail_answer()
            suppress_sources = True
        elif is_compensation_question(question):
            answer = compensation_guardrail_answer(question)
            suppress_sources = True
        else:
            vector, embedding_latency = embed_query(env, question)
            chunks, search_latency, search_debug = search_chunks(env, question, vector, top_k, mode, filter_expr)
            answer, answer_latency, llm_debug = generate_answer(env, question, chunks)
            answer = clean_user_answer(answer)
    except Exception as exc:
        status = "failed"
        error = str(exc)
    total_latency = (time.perf_counter() - total_start) * 1000
    sources = [] if suppress_sources else [
        {
            "page_id": c.get("page_id"),
            "section_id": c.get("section_id"),
            "title": c.get("title"),
            "source_url": c.get("source_url"),
            "chunk_index": c.get("chunk_index"),
            "score": c.get("@search.score"),
        }
        for c in chunks
    ]
    return {
        "user": {"question": question, "answer": answer, "sources": sources},
        "debug": {
            "search_mode": mode,
            "top_k": top_k,
            "filter": filter_expr,
            "retrieved_chunks": [
                {**sources[i], "snippet": chunks[i].get("content", "")[:500]} for i in range(len(chunks))
            ],
            "search_request": search_debug,
            "prompt_preview": llm_debug.get("prompt_preview"),
            "llm_usage": llm_debug.get("usage", {}),
        },
        "observability": {
            "status": status,
            "error": error,
            "timestamp": now_iso(),
            "index_name": env.get("AZURE_SEARCH_INDEX_NAME"),
            "embedding_deployment": env.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            "chat_deployment": env.get("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            "embedding_latency_ms": round(embedding_latency, 2),
            "search_latency_ms": round(search_latency, 2),
            "answer_latency_ms": round(answer_latency, 2),
            "total_latency_ms": round(total_latency, 2),
            "retrieved_chunk_count": len(chunks),
            "source_page_ids": [s["page_id"] for s in sources],
        },
    }


def write_report(results: list[dict[str, Any]]) -> None:
    lines = ["# Answer Generation Test Report\n", f"Generated at: {now_iso()}\n\n"]
    for i, result in enumerate(results, 1):
        lines.append(f"## {i}. {result['user']['question']}\n")
        lines.append(f"Status: {result['observability']['status']}\n\n")
        lines.append(result['user']['answer'][:2000] + "\n\n")
        lines.append("Sources:\n")
        for s in result['user']['sources'][:5]:
            lines.append(f"- {s['page_id']} | {s['source_url']} | score={s['score']}\n")
        lines.append("\n")
    REPORT_PATH.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate grounded RAG answers from Azure AI Search.")
    parser.add_argument("--question")
    parser.add_argument("--questions-file", default=str(Path(__file__).resolve().with_name("answer_test_questions.json")))
    parser.add_argument("--mode", default="hybrid", choices=["keyword", "vector", "hybrid"])
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--filter")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    questions = []
    if args.question:
        questions = [args.question]
    else:
        questions = json.loads(Path(args.questions_file).read_text(encoding="utf-8"))["questions"]

    results = [answer_question(q, args.mode, args.top_k, args.filter) for q in questions]
    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(results)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print("\nQUESTION:", result["user"]["question"])
            print("STATUS:", result["observability"]["status"])
            if result["observability"].get("error"):
                print("ERROR:", result["observability"]["error"])
            print("ANSWER:\n", result["user"]["answer"])
            print("SOURCES:")
            for source in result["user"]["sources"][:5]:
                print(f"- {source['page_id']} | {source['source_url']} | score={source['score']}")
            print("OBSERVABILITY:", json.dumps(result["observability"], indent=2))
    return 0 if all(r["observability"]["status"] == "success" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
