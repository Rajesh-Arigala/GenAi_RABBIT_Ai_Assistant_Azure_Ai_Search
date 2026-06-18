"""Flask UI for the V4 Business-Tech RAG assistant.

Modes:
- User Mode: polished answer + sources
- Debug Mode: retrieval/evidence/prompt details
- Observability Mode: latency/health/metrics
- Tech Mode: placeholder for future deep diagnostics
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[0]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
ENV_PATH = PROJECT_ROOT / ".env"


def _load_dotenv() -> dict[str, str]:
    values: dict[str, str] = {}
    if ENV_PATH.exists():
        for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


LOCAL_ENV = _load_dotenv()

ANSWER_DIR = PROJECT_ROOT / "17_answer_generation"
if str(ANSWER_DIR) not in sys.path:
    sys.path.insert(0, str(ANSWER_DIR))

from rag_answer_v1 import answer_question  # noqa: E402

app = Flask(__name__)

PRODUCT_NAME = "RABBIT Assistant"
ASSISTANT_NAME = 'Raj AI Business and Beyond Intelligence Tech "Assistant"'
PROFILE_NAME = "Rajesh Arigala"


@app.get("/")
def index():
    return render_template(
        "index.html",
        product_name=PRODUCT_NAME,
        assistant_name=ASSISTANT_NAME,
        profile_name=PROFILE_NAME,
    )


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "business-tech-rag-flask-ui",
        "assistant_name": ASSISTANT_NAME,
    }


@app.get("/api/config")
def config():
    return {
        "product_name": PRODUCT_NAME,
        "assistant_name": ASSISTANT_NAME,
        "profile_name": PROFILE_NAME,
        "default_mode": "user",
        "default_search_mode": "hybrid",
        "default_top_k": 5,
        "modes": ["user", "debug", "observability", "tech"],
        "tech_mode_status": "placeholder",
    }


@app.post("/api/chat")
def chat():
    started = time.perf_counter()
    request_id = f"req_{uuid.uuid4().hex[:16]}"
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question") or "").strip()
    mode = str(payload.get("mode") or "user").strip().lower()
    search_mode = str(payload.get("search_mode") or "hybrid").strip().lower()
    session_id = str(payload.get("session_id") or f"sess_{uuid.uuid4().hex[:10]}").strip()
    turn_id = str(payload.get("turn_id") or f"turn_{int(time.time() * 1000)}").strip()
    top_k = int(payload.get("top_k") or 5)
    filter_expr = payload.get("filter") or None
    debug_password = str(payload.get("debug_password") or "")

    expected_mode_password = LOCAL_ENV.get("FLASK_MODE_PASSWORD") or LOCAL_ENV.get("FLASK_DEBUG_PASSWORD", "")
    if mode != "user" and expected_mode_password and debug_password != expected_mode_password:
        return jsonify({"status": "forbidden", "error": "Owner/demo password is required or invalid for this mode."}), 403

    if not question:
        return jsonify({"status": "error", "error": "Question is required."}), 400

    _log("chat_request_received", request_id, session_id, turn_id, {"mode": mode, "search_mode": search_mode, "top_k": top_k})

    try:
        result = answer_question(question, mode=search_mode, top_k=top_k, filter_expr=filter_expr)
        full_payload = _shape_response(result, request_id, session_id, turn_id, mode, search_mode, top_k, filter_expr, started)
        _log("answer_returned", request_id, session_id, turn_id, full_payload["observability"])
        return jsonify(full_payload)
    except Exception as exc:  # noqa: BLE001 - controlled UI error payload
        error_payload = _error_payload(str(exc), request_id, session_id, turn_id, mode, search_mode, started)
        _log("error_occurred", request_id, session_id, turn_id, error_payload)
        return jsonify(error_payload), 500


def _shape_response(result: dict, request_id: str, session_id: str, turn_id: str, ui_mode: str, search_mode: str, top_k: int, filter_expr: str | None, started: float) -> dict:
    user = result.get("user", {})
    debug = result.get("debug", {})
    observability = result.get("observability", {})
    sources = user.get("sources", []) or []
    retrieved = debug.get("retrieved_chunks", []) or []
    scored_chunks = _add_relative_scores(retrieved)
    scores = [c.get("retrieval_score_raw") for c in scored_chunks if isinstance(c.get("retrieval_score_raw"), (int, float))]
    llm_confidence = _estimate_answer_confidence(user.get("answer", ""), scored_chunks, observability)

    user_block = {
        "question": user.get("question"),
        "answer": user.get("answer", ""),
        "links": _public_links(sources),
        "answer_confidence_label": llm_confidence["label"],
        "answer_confidence_score": llm_confidence["score"],
        "answer_confidence_reason": llm_confidence["reason"],
        "sources": sources,
        "suggested_followups": _suggest_followups(user.get("question", "")),
    }

    debug_block = {
        "search_mode": search_mode,
        "top_k": top_k,
        "filter": filter_expr,
        "retrieved_chunks": scored_chunks,
        "search_request": debug.get("search_request"),
        "prompt_preview": debug.get("prompt_preview"),
        "llm_usage": debug.get("llm_usage", {}),
        "answer_confidence": llm_confidence,
        "source_lineage": _source_lineage(sources),
    }

    observability_block = {
        **observability,
        "request_id": request_id,
        "session_id": session_id,
        "turn_id": turn_id,
        "ui_mode": ui_mode,
        "search_mode": search_mode,
        "filter_applied": filter_expr,
        "top_k": top_k,
        "question_length_chars": len(user.get("question") or ""),
        "question_hash": _sha256(user.get("question") or ""),
        "answer_hash": _sha256(user.get("answer") or ""),
        "top_1_score": max(scores) if scores else None,
        "min_retrieval_score": min(scores) if scores else None,
        "max_retrieval_score": max(scores) if scores else None,
        "score_spread": round((max(scores) - min(scores)), 8) if scores else None,
        "average_score": round(sum(scores) / len(scores), 8) if scores else None,
        "source_diversity_count": len(set(observability.get("source_page_ids") or [])),
        "flask_total_latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "answer_confidence_label": llm_confidence["label"],
        "answer_confidence_score": llm_confidence["score"],
    }

    traceability_block = {
        "request_id": request_id,
        "session_id": session_id,
        "turn_id": turn_id,
        "index_name": observability.get("index_name"),
        "embedding_deployment": observability.get("embedding_deployment"),
        "chat_deployment": observability.get("chat_deployment"),
        "page_ids_used": [s.get("page_id") for s in sources],
        "section_ids_used": [s.get("section_id") for s in sources],
        "source_urls_used": [s.get("source_url") for s in sources],
        "chunk_ids_used": [c.get("chunk_id") for c in scored_chunks if c.get("chunk_id")],
        "prompt_template": "17_answer_generation/answer_prompt_template.md",
        "profile_context": "10_working_docs/profile_positioning_prompt_template.md",
    }

    return {
        "status": observability.get("status", "success"),
        "user": user_block,
        "debug": debug_block,
        "observability": observability_block,
        "tech": {
            "status": "planned",
            "message": "Tech Mode is a placeholder. Raw API payloads, registry diagnostics, schema diagnostics, and deployment internals will be added later.",
            "available_now": ["request_id", "session_id", "turn_id", "source lineage", "mode contract"],
        },
        "traceability": traceability_block,
        "logging": {
            "chat_events_log": str(LOG_DIR / "chat_events.jsonl"),
            "error_events_log": str(LOG_DIR / "error_events.jsonl"),
            "observability_events_log": str(LOG_DIR / "observability_events.jsonl"),
        },
    }


def _public_links(sources: list[dict], limit: int = 2) -> list[dict]:
    links = []
    seen = set()
    for source in sources:
        url = source.get("source_url")
        if not url or url in seen:
            continue
        seen.add(url)
        links.append({
            "page_id": source.get("page_id"),
            "title": source.get("title") or source.get("page_id") or url,
            "source_url": url,
        })
        if len(links) >= limit:
            break
    return links


def _add_relative_scores(chunks: list[dict]) -> list[dict]:
    raw_scores = [c.get("score") for c in chunks if isinstance(c.get("score"), (int, float))]
    top = max(raw_scores) if raw_scores else None
    shaped = []
    for idx, chunk in enumerate(chunks, 1):
        score = chunk.get("score")
        relative = round((score / top) * 100, 2) if top and isinstance(score, (int, float)) else None
        shaped.append({
            **chunk,
            "rank": idx,
            "retrieval_score_raw": score,
            "hybrid_score_raw": score,
            "vector_score_raw": None,
            "keyword_score_raw": None,
            "retrieval_score_relative_percent": relative,
            "score_note": "Azure returned @search.score. Separate vector/keyword sub-scores are not exposed in this response.",
        })
    return shaped


def _estimate_answer_confidence(answer: str, chunks: list[dict], observability: dict) -> dict:
    if observability.get("status") != "success" or not answer.strip():
        return {"label": "low", "score": 0.0, "reason": "Answer generation failed or returned no answer."}
    if len(chunks) >= 3:
        return {"label": "high", "score": 0.86, "reason": "Answer generated from multiple retrieved source chunks. This is an LLM self-assessment proxy, not a statistical probability."}
    if chunks:
        return {"label": "medium", "score": 0.68, "reason": "Answer generated from limited retrieved evidence."}
    return {"label": "low", "score": 0.35, "reason": "No retrieved chunks were available."}


def _source_lineage(sources: list[dict]) -> list[dict]:
    return [{
        "page_id": s.get("page_id"),
        "section_id": s.get("section_id"),
        "source_url": s.get("source_url"),
        "chunk_index": s.get("chunk_index"),
        "score": s.get("score"),
    } for s in sources]


def _suggest_followups(question: str) -> list[str]:
    q = question.lower()
    if "bpcl" in q:
        return ["How does BPCL experience connect to MLOps reliability?", "Show business-tech role fit from BPCL."]
    if "kubernetes" in q or "mlops" in q:
        return ["Which projects show production deployment?", "Show the strongest MLOps evidence."]
    return ["Show business-tech hybrid role fit.", "Which projects best prove AI transformation capability?"]


def _error_payload(message: str, request_id: str, session_id: str, turn_id: str, ui_mode: str, search_mode: str, started: float) -> dict:
    return {
        "status": "failed",
        "user": {"answer": "The assistant could not complete the request.", "sources": []},
        "debug": {"error": message},
        "observability": {
            "status": "failed",
            "error": message,
            "request_id": request_id,
            "session_id": session_id,
            "turn_id": turn_id,
            "ui_mode": ui_mode,
            "search_mode": search_mode,
            "flask_total_latency_ms": round((time.perf_counter() - started) * 1000, 2),
        },
        "tech": {"status": "planned", "message": "Tech Mode placeholder."},
        "traceability": {"request_id": request_id, "session_id": session_id, "turn_id": turn_id},
    }


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest() if value else ""


def _log(event_type: str, request_id: str, session_id: str, turn_id: str, metadata: dict) -> None:
    record = {
        "event_id": f"evt_{uuid.uuid4().hex[:16]}",
        "event_type": event_type,
        "request_id": request_id,
        "session_id": session_id,
        "turn_id": turn_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
    }
    target = "error_events.jsonl" if "error" in event_type else "observability_events.jsonl" if event_type == "answer_returned" else "chat_events.jsonl"
    with (LOG_DIR / target).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8091"))
    app.run(host="0.0.0.0", port=port, debug=False)
