#!/usr/bin/env python3
"""Create Azure AI Search index and upload vectorized chunk documents."""

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
REPORT_DIR = ROOT / "15_azure_search_upload"


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


def build_ssl_context() -> ssl.SSLContext:
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def request_json(method: str, url: str, api_key: str, payload: Any | None = None, retries: int = 4) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    context = build_ssl_context()
    last_error = ""
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=180, context=context) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw) if raw else {}
                return response.status, body
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {raw[:1000]}"
            if exc.code not in {408, 429, 500, 502, 503, 504}:
                raise RuntimeError(last_error)
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(2 * attempt)
    raise RuntimeError(f"Request failed after {retries} attempts: {last_error}")


def endpoint_url(endpoint: str, path: str, api_version: str) -> str:
    endpoint = endpoint.rstrip("/")
    return f"{endpoint}{path}?api-version={urllib.parse.quote(api_version)}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def create_index(env: dict[str, str], recreate: bool) -> dict[str, Any]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_key = required(env, "AZURE_SEARCH_API_KEY")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    schema_path = Path(required(env, "AZURE_INDEX_SCHEMA"))
    schema = load_json(schema_path)
    schema["name"] = index_name

    if recreate:
        delete_url = endpoint_url(endpoint, f"/indexes/{index_name}", api_version)
        try:
            request_json("DELETE", delete_url, api_key, None)
        except RuntimeError as exc:
            if "HTTP 404" not in str(exc):
                raise

    url = endpoint_url(endpoint, f"/indexes/{index_name}", api_version)
    status, body = request_json("PUT", url, api_key, schema)
    result = {
        "action": "create-index",
        "created_at": now_iso(),
        "endpoint": endpoint,
        "index_name": index_name,
        "schema_path": str(schema_path),
        "http_status": status,
        "field_count": len(body.get("fields", [])),
        "vector_search": body.get("vectorSearch"),
    }
    write_json(REPORT_DIR / "azure_search_create_index_result.json", result)
    return result


def get_index(env: dict[str, str]) -> dict[str, Any]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_key = required(env, "AZURE_SEARCH_API_KEY")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    url = endpoint_url(endpoint, f"/indexes/{index_name}", api_version)
    status, body = request_json("GET", url, api_key, None)
    return {"http_status": status, "index": body}


def upload_docs(env: dict[str, str], batch_size: int) -> dict[str, Any]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_key = required(env, "AZURE_SEARCH_API_KEY")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    docs_path = ROOT / "14_output_embeddings" / "azure_upload_documents_with_vectors_batch_v1.json"
    payload = load_json(docs_path)
    raw_docs = payload["value"]
    schema_path = Path(required(env, "AZURE_INDEX_SCHEMA"))
    schema = load_json(schema_path)
    allowed_fields = {field["name"] for field in schema["fields"]}
    docs = [
        {key: value for key, value in doc.items() if key.startswith("@search.") or key in allowed_fields}
        for doc in raw_docs
    ]
    url = endpoint_url(endpoint, f"/indexes/{index_name}/docs/index", api_version)

    uploaded = 0
    failed: list[dict[str, Any]] = []
    batches = [docs[i:i + batch_size] for i in range(0, len(docs), batch_size)]
    for idx, batch in enumerate(batches, start=1):
        status, body = request_json("POST", url, api_key, {"value": batch})
        results = body.get("value", [])
        batch_failed = [item for item in results if not (item.get("succeeded") is True or item.get("status") is True)]
        if batch_failed:
            failed.append({"batch_index": idx, "http_status": status, "failed": batch_failed})
        uploaded += sum(1 for item in results if item.get("succeeded") is True or item.get("status") is True)

    result = {
        "action": "upload-docs",
        "created_at": now_iso(),
        "endpoint": endpoint,
        "index_name": index_name,
        "source_path": str(docs_path),
        "input_documents": len(raw_docs),
        "schema_filtered_documents": len(docs),
        "uploaded_documents": uploaded,
        "failed_documents": sum(len(item["failed"]) for item in failed),
        "failed_batches": failed,
    }
    write_json(REPORT_DIR / "azure_search_upload_result.json", result)
    return result


def count_docs(env: dict[str, str]) -> dict[str, Any]:
    endpoint = required(env, "AZURE_SEARCH_ENDPOINT")
    api_key = required(env, "AZURE_SEARCH_API_KEY")
    api_version = required(env, "AZURE_SEARCH_API_VERSION")
    index_name = required(env, "AZURE_SEARCH_INDEX_NAME")
    url = endpoint_url(endpoint, f"/indexes/{index_name}/docs/$count", api_version)
    status, body = request_json("GET", url, api_key, None)
    return {"http_status": status, "index_name": index_name, "count": body}


def main() -> int:
    parser = argparse.ArgumentParser(description="Azure AI Search admin for V4 RAG corpus.")
    sub = parser.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create-index")
    create_parser.add_argument("--recreate", action="store_true")
    sub.add_parser("get-index")
    upload_parser = sub.add_parser("upload-docs")
    upload_parser.add_argument("--batch-size", type=int, default=50)
    sub.add_parser("count")
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    if args.command == "create-index":
        print(json.dumps(create_index(env, args.recreate), indent=2, ensure_ascii=False))
    elif args.command == "get-index":
        result = get_index(env)
        print(json.dumps({"http_status": result["http_status"], "name": result["index"].get("name"), "fields": len(result["index"].get("fields", []))}, indent=2))
    elif args.command == "upload-docs":
        print(json.dumps(upload_docs(env, args.batch_size), indent=2, ensure_ascii=False))
    elif args.command == "count":
        print(json.dumps(count_docs(env), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
