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
CONFIG_DIR = PROJECT_ROOT / "01_input_seed_and_config"
CHUNK_DIR = PROJECT_ROOT / "09_future_output_chunks"
RAG_READY_DIR = PROJECT_ROOT / "06_output_rag_documents_ready"
RAG_STAGING_DIR = PROJECT_ROOT / "06_output_rag_documents"
HIERARCHY_REGISTRY_PATH = CONFIG_DIR / "hierarchy_registry.json"
DOCUMENT_REGISTRY_PATH = CONFIG_DIR / "document_registry.json"
CHUNK_REGISTRY_PATH = CHUNK_DIR / "chunk_registry.json"
APPROVED_CHUNKS_PATH = CHUNK_DIR / "approved_chunks_v1.jsonl"
LIFECYCLE_LOG_PATH = LOG_DIR / "lifecycle_events.jsonl"


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


@app.get("/api/lifecycle/summary")
def lifecycle_summary():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    payload = _lifecycle_payload(include_chunks=False)
    payload["observability"] = _lifecycle_observability("summary_read", request_id, started, "success")
    payload["traceability"] = _lifecycle_traceability(request_id, None, "summary_read")
    _log_lifecycle_event("summary_read", request_id, None, "success", payload["observability"], mutation=False)
    return jsonify(payload)


@app.get("/api/lifecycle/hierarchy")
def lifecycle_hierarchy():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    hierarchy = _lifecycle_payload(include_chunks=False)["hierarchy"]
    return jsonify({
        "hierarchy": hierarchy,
        "observability": _lifecycle_observability("hierarchy_read", request_id, started, "success"),
        "traceability": _lifecycle_traceability(request_id, None, "hierarchy_read"),
    })


@app.get("/api/lifecycle/documents")
def lifecycle_documents():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    payload = _lifecycle_payload(include_chunks=False)
    return jsonify({
        "documents": payload["documents"],
        "counts": payload["counts"],
        "observability": _lifecycle_observability("documents_read", request_id, started, "success"),
        "traceability": _lifecycle_traceability(request_id, None, "documents_read"),
    })


@app.get("/api/lifecycle/chunks")
def lifecycle_chunks():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    page_id = str(request.args.get("page_id") or "").strip()
    chunks = _load_chunks_by_page().get(page_id, []) if page_id else []
    return jsonify({
        "page_id": page_id,
        "chunk_count": len(chunks),
        "chunks": chunks[:50],
        "truncated": len(chunks) > 50,
        "observability": _lifecycle_observability("chunks_read", request_id, started, "success", page_id=page_id, record_count=len(chunks)),
        "traceability": _lifecycle_traceability(request_id, page_id, "chunks_read"),
    })


@app.get("/api/lifecycle/versions")
def lifecycle_versions():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    page_id = str(request.args.get("page_id") or "").strip()
    docs = {d.get("page_id"): d for d in _load_document_registry().get("documents", [])}
    doc = docs.get(page_id)
    if not doc:
        return jsonify({
            "page_id": page_id,
            "versions": [],
            "message": "No document attached to this hierarchy slot.",
            "observability": _lifecycle_observability("versions_read", request_id, started, "empty", page_id=page_id, record_count=0),
            "traceability": _lifecycle_traceability(request_id, page_id, "versions_read"),
        })
    versions = [{
        "version": doc.get("version", 1),
        "status": doc.get("document_status"),
        "content_hash_sha256": doc.get("content_hash_sha256"),
        "rag_file_name": doc.get("rag_file_name"),
        "word_count": doc.get("word_count"),
        "chunking_status": doc.get("chunking_status"),
        "indexing_status": doc.get("indexing_status"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }]
    return jsonify({
        "page_id": page_id,
        "document_id": doc.get("document_id"),
        "versions": versions,
        "observability": _lifecycle_observability("versions_read", request_id, started, "success", page_id=page_id, record_count=len(versions)),
        "traceability": _lifecycle_traceability(request_id, page_id, "versions_read"),
    })


@app.post("/api/lifecycle/action")
def lifecycle_action():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action") or "").strip().lower()
    page_id = str(payload.get("page_id") or "").strip()
    debug_password = str(payload.get("debug_password") or "")
    expected_mode_password = LOCAL_ENV.get("FLASK_MODE_PASSWORD") or LOCAL_ENV.get("FLASK_DEBUG_PASSWORD", "")
    if expected_mode_password and debug_password != expected_mode_password:
        obs = _lifecycle_observability(action or "unknown_action", request_id, started, "forbidden", page_id=page_id)
        _log_lifecycle_event(action or "unknown_action", request_id, page_id, "forbidden", obs, mutation=False, error="Invalid lifecycle password")
        return jsonify({"status": "forbidden", "error": "Owner/demo password is required or invalid for lifecycle actions.", "observability": obs, "traceability": _lifecycle_traceability(request_id, page_id, action)}), 403
    allowed = {
        "upload_document", "replace_document", "delete_document_content", "rechunk_document",
        "approve_chunks", "export_azure", "sync_azure", "view_versions"
    }
    if action not in allowed:
        obs = _lifecycle_observability(action or "unsupported_action", request_id, started, "error", page_id=page_id)
        _log_lifecycle_event(action or "unsupported_action", request_id, page_id, "error", obs, mutation=False, error="Unsupported lifecycle action")
        return jsonify({"status": "error", "error": "Unsupported lifecycle action.", "observability": obs, "traceability": _lifecycle_traceability(request_id, page_id, action)}), 400
    if not page_id:
        obs = _lifecycle_observability(action, request_id, started, "error")
        _log_lifecycle_event(action, request_id, None, "error", obs, mutation=False, error="page_id is required")
        return jsonify({"status": "error", "error": "page_id is required.", "observability": obs, "traceability": _lifecycle_traceability(request_id, None, action)}), 400
    snapshot = _lifecycle_page_snapshot(page_id)
    obs = _lifecycle_observability(action, request_id, started, "logged_not_executed", page_id=page_id, record_count=snapshot.get("chunk_count"))
    record = _log_lifecycle_event(
        action,
        request_id,
        page_id,
        "logged_not_executed",
        obs,
        mutation=False,
        metadata={k: v for k, v in payload.items() if k not in {"debug_password"}},
        before_state=snapshot,
        after_state={"mutation_status": "not_executed", "reason": "Guarded first pass records intent only."},
    )
    return jsonify({
        "status": "logged_not_executed",
        "message": f"Lifecycle action '{action}' was recorded for {page_id}. No files or Azure records were changed in this guarded pass.",
        "event": record,
        "observability": obs,
        "traceability": _lifecycle_traceability(request_id, page_id, action),
    })


@app.get("/api/lifecycle/logs")
def lifecycle_logs():
    started = time.perf_counter()
    request_id = f"life_req_{uuid.uuid4().hex[:16]}"
    limit = min(int(request.args.get("limit") or 50), 200)
    records = []
    if LIFECYCLE_LOG_PATH.exists():
        lines = LIFECYCLE_LOG_PATH.read_text(encoding="utf-8").splitlines()[-limit:]
        records = [json.loads(line) for line in lines if line.strip()]
    return jsonify({
        "records": records,
        "count": len(records),
        "log_path": str(LIFECYCLE_LOG_PATH),
        "observability": _lifecycle_observability("logs_read", request_id, started, "success", record_count=len(records)),
        "traceability": _lifecycle_traceability(request_id, None, "logs_read"),
    })


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


def _read_json(path: Path, default: dict | list | None = None):
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_hierarchy_registry() -> dict:
    return _read_json(HIERARCHY_REGISTRY_PATH, {})


def _load_document_registry() -> dict:
    return _read_json(DOCUMENT_REGISTRY_PATH, {"documents": [], "counts": {}})


def _load_chunks_by_page() -> dict[str, list[dict]]:
    by_page: dict[str, list[dict]] = {}
    if not APPROVED_CHUNKS_PATH.exists():
        return by_page
    with APPROVED_CHUNKS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunk = json.loads(line)
            page_id = chunk.get("page_id") or "unknown"
            by_page.setdefault(page_id, []).append({
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "page_id": page_id,
                "section_id": chunk.get("section_id"),
                "title": chunk.get("title"),
                "source_url": chunk.get("source_url"),
                "chunk_index": chunk.get("chunk_index"),
                "chunk_total": chunk.get("chunk_total"),
                "word_count": chunk.get("word_count"),
                "token_estimate": chunk.get("token_estimate"),
                "review_status": chunk.get("review_status"),
                "indexing_status": chunk.get("indexing_status"),
                "chunking_version": chunk.get("chunking_version"),
                "content_preview": (chunk.get("content") or "")[:420],
            })
    return by_page


def _lifecycle_payload(include_chunks: bool = False) -> dict:
    hierarchy = _load_hierarchy_registry()
    doc_registry = _load_document_registry()
    chunks_by_page = _load_chunks_by_page()
    documents = doc_registry.get("documents", [])
    docs_by_page = {d.get("page_id"): d for d in documents}
    nodes = []
    for node in hierarchy.get("nodes", []):
        page_id = node.get("page_id")
        doc = docs_by_page.get(page_id)
        page_chunks = chunks_by_page.get(page_id, [])
        nodes.append({
            "page_id": page_id,
            "title": node.get("title"),
            "expected_url": node.get("expected_url"),
            "parent_page_id": node.get("parent_page_id"),
            "depth": node.get("depth"),
            "section_id": node.get("section_id"),
            "node_type": node.get("node_type"),
            "slot_status": node.get("slot_status"),
            "document_status": (doc or {}).get("document_status", node.get("document_status")),
            "chunking_status": (doc or {}).get("chunking_status", (node.get("current_document") or {}).get("chunking_status")),
            "indexing_status": (doc or {}).get("indexing_status", (node.get("current_document") or {}).get("indexing_status")),
            "children": node.get("children", []),
            "has_document": bool(doc),
            "document_id": (doc or {}).get("document_id"),
            "version": (doc or {}).get("version"),
            "word_count": (doc or {}).get("word_count"),
            "char_count": (doc or {}).get("char_count"),
            "file_size_bytes": (doc or {}).get("file_size_bytes"),
            "rag_file_name": (doc or {}).get("rag_file_name"),
            "rag_ready_path": (doc or {}).get("rag_ready_path"),
            "content_hash_sha256": (doc or {}).get("content_hash_sha256"),
            "chunk_count": len(page_chunks),
            "approved_chunk_count": sum(1 for c in page_chunks if c.get("review_status") == "approved"),
            "ready_for_indexing_count": sum(1 for c in page_chunks if c.get("indexing_status") == "ready_for_indexing"),
            "notes": node.get("notes"),
        })
    ready_dir_count = len(list(RAG_READY_DIR.glob("*_rag.txt"))) if RAG_READY_DIR.exists() else 0
    staging_dir_count = len(list(RAG_STAGING_DIR.glob("*_rag.txt"))) if RAG_STAGING_DIR.exists() else 0
    total_chunks = sum(len(v) for v in chunks_by_page.values())
    counts = {
        **(hierarchy.get("counts") or {}),
        **{f"document_registry_{k}": v for k, v in (doc_registry.get("counts") or {}).items()},
        "canonical_ready_documents_count": ready_dir_count,
        "staging_rag_documents_count": staging_dir_count,
        "approved_chunks_count": total_chunks,
        "chunked_pages_count": len(chunks_by_page),
        "placeholder_slots_without_documents": sum(1 for n in nodes if not n["has_document"]),
    }
    payload = {
        "status": "ready",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": counts,
        "hierarchy": {
            "registry_version": hierarchy.get("registry_version"),
            "lifecycle_rules": hierarchy.get("lifecycle_rules", {}),
            "nodes": nodes,
        },
        "documents": documents,
        "paths": {
            "hierarchy_registry": str(HIERARCHY_REGISTRY_PATH),
            "document_registry": str(DOCUMENT_REGISTRY_PATH),
            "approved_chunks": str(APPROVED_CHUNKS_PATH),
            "lifecycle_log": str(LIFECYCLE_LOG_PATH),
        },
    }
    if include_chunks:
        payload["chunks_by_page"] = chunks_by_page
    return payload


def _lifecycle_observability(action: str, request_id: str, started: float, status: str, page_id: str | None = None, record_count: int | None = None) -> dict:
    return {
        "request_id": request_id,
        "action": action,
        "status": status,
        "page_id": page_id,
        "record_count": record_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "hierarchy_registry_exists": HIERARCHY_REGISTRY_PATH.exists(),
        "document_registry_exists": DOCUMENT_REGISTRY_PATH.exists(),
        "approved_chunks_exists": APPROVED_CHUNKS_PATH.exists(),
        "lifecycle_log_path": str(LIFECYCLE_LOG_PATH),
        "mutation_mode": "guarded_log_only",
    }


def _lifecycle_traceability(request_id: str, page_id: str | None, action: str | None) -> dict:
    return {
        "request_id": request_id,
        "page_id": page_id,
        "action": action,
        "hierarchy_registry": str(HIERARCHY_REGISTRY_PATH),
        "document_registry": str(DOCUMENT_REGISTRY_PATH),
        "chunk_registry": str(CHUNK_REGISTRY_PATH),
        "approved_chunks": str(APPROVED_CHUNKS_PATH),
        "lifecycle_log": str(LIFECYCLE_LOG_PATH),
        "source_of_truth": "hierarchy_registry + document_registry + approved_chunks",
    }


def _lifecycle_page_snapshot(page_id: str) -> dict:
    payload = _lifecycle_payload(include_chunks=False)
    node = next((n for n in payload["hierarchy"]["nodes"] if n.get("page_id") == page_id), None)
    chunks = _load_chunks_by_page().get(page_id, [])
    return {
        "page_id": page_id,
        "node_found": bool(node),
        "document_id": (node or {}).get("document_id"),
        "title": (node or {}).get("title"),
        "slot_status": (node or {}).get("slot_status"),
        "document_status": (node or {}).get("document_status"),
        "chunking_status": (node or {}).get("chunking_status"),
        "indexing_status": (node or {}).get("indexing_status"),
        "version": (node or {}).get("version"),
        "word_count": (node or {}).get("word_count"),
        "chunk_count": len(chunks),
        "approved_chunk_count": sum(1 for c in chunks if c.get("review_status") == "approved"),
    }


def _log_lifecycle_event(event_type: str, request_id: str, page_id: str | None, status: str, observability: dict, mutation: bool, metadata: dict | None = None, before_state: dict | None = None, after_state: dict | None = None, error: str | None = None) -> dict:
    record = {
        "event_id": f"life_{uuid.uuid4().hex[:16]}",
        "event_type": event_type,
        "request_id": request_id,
        "page_id": page_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "mutation_executed": mutation,
        "error": error,
        "observability": observability,
        "traceability": _lifecycle_traceability(request_id, page_id, event_type),
        "before_state": before_state,
        "after_state": after_state,
        "metadata": metadata or {},
    }
    with LIFECYCLE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


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
