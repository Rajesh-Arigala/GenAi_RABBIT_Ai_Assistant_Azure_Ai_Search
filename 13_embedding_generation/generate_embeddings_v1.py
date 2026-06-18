#!/usr/bin/env python3
"""Generate Azure OpenAI embeddings for Azure-shaped chunk documents."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Missing .env file: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def required(env: dict[str, str], key: str) -> str:
    value = env.get(key) or os.environ.get(key)
    if not value:
        raise ValueError(f"Missing required environment value: {key}")
    return value


def build_embeddings_url(endpoint: str, deployment: str, api_version: str) -> str:
    endpoint = endpoint.rstrip("/")
    return f"{endpoint}/openai/deployments/{deployment}/embeddings?api-version={api_version}"


def call_embeddings(
    url: str,
    api_key: str,
    inputs: list[str],
    max_retries: int,
    retry_sleep_seconds: float,
    ssl_context: ssl.SSLContext,
) -> list[list[float]]:
    payload = json.dumps({"input": inputs}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    last_error = ""
    for attempt in range(1, max_retries + 1):
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=120, context=ssl_context) as response:
                body = json.loads(response.read().decode("utf-8"))
            data = sorted(body["data"], key=lambda item: item["index"])
            return [item["embedding"] for item in data]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {detail[:500]}"
            if exc.code not in {408, 429, 500, 502, 503, 504}:
                break
        except Exception as exc:  # network/transient client exceptions
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < max_retries:
            time.sleep(retry_sleep_seconds * attempt)
    raise RuntimeError(f"Embedding request failed after {max_retries} attempts: {last_error}")


def build_ssl_context(env: dict[str, str]) -> ssl.SSLContext:
    ca_bundle = env.get("AZURE_OPENAI_CA_BUNDLE") or os.environ.get("AZURE_OPENAI_CA_BUNDLE")
    if ca_bundle:
        return ssl.create_default_context(cafile=ca_bundle)
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def batches(rows: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def validate_vectors(rows: list[dict[str, Any]], expected_dimensions: int) -> dict[str, Any]:
    missing = [row["id"] for row in rows if "content_vector" not in row]
    wrong_dimensions = [
        {"id": row["id"], "dimensions": len(row.get("content_vector", []))}
        for row in rows
        if "content_vector" in row and len(row["content_vector"]) != expected_dimensions
    ]
    empty_content = [row["id"] for row in rows if not row.get("content", "").strip()]
    return {
        "documents_total": len(rows),
        "missing_vectors": missing,
        "wrong_dimension_vectors": wrong_dimensions,
        "empty_content_documents": empty_content,
        "expected_dimensions": expected_dimensions,
        "all_vectors_valid": not missing and not wrong_dimensions and not empty_content,
    }


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Embedding Generation Report\n",
        f"Generated at: {manifest['generated_at']}\n\n",
        "## Status\n",
        f"- status: {manifest['status']}\n",
        f"- embedding_deployment: {manifest['embedding_deployment']}\n",
        f"- embedding_dimensions: {manifest['embedding_dimensions']}\n\n",
        "## Counts\n",
    ]
    for key, value in manifest["counts"].items():
        lines.append(f"- {key}: {value}\n")
    lines.append("\n## Validation\n")
    for key, value in manifest["validation"].items():
        if isinstance(value, list):
            lines.append(f"- {key}: {len(value)}\n")
        else:
            lines.append(f"- {key}: {value}\n")
    lines.append("\n## Next Step\n")
    lines.append("- Step 7: create or update the Azure AI Search index using the schema from `13_output_azure_ready`.\n")
    lines.append("- Step 8: upload `azure_upload_documents_with_vectors_batch_v1.json` to Azure AI Search.\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate embeddings for Azure AI Search upload documents.")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--limit", type=int, default=0, help="Optional smoke-test limit for number of documents.")
    parser.add_argument("--max-retries", type=int, default=4)
    parser.add_argument("--retry-sleep-seconds", type=float, default=2.0)
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    endpoint = required(env, "AZURE_OPENAI_ENDPOINT")
    api_key = required(env, "AZURE_OPENAI_API_KEY")
    api_version = required(env, "AZURE_OPENAI_API_VERSION")
    deployment = required(env, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    expected_dimensions = int(required(env, "AZURE_OPENAI_EMBEDDING_DIMENSIONS"))
    input_path = Path(required(env, "AZURE_READY_INPUT_JSONL"))
    output_dir = Path(required(env, "EMBEDDING_OUTPUT_DIR"))
    output_dir.mkdir(parents=True, exist_ok=True)

    output_jsonl = output_dir / "azure_upload_documents_with_vectors_v1.jsonl"
    output_batch = output_dir / "azure_upload_documents_with_vectors_batch_v1.json"
    manifest_path = output_dir / "embedding_manifest.json"
    report_path = output_dir / "embedding_report.md"

    url = build_embeddings_url(endpoint, deployment, api_version)
    docs = read_jsonl(input_path)
    if args.limit:
        docs = docs[: args.limit]
    vectorized: list[dict[str, Any]] = []
    failed_batches: list[dict[str, Any]] = []
    started = now_iso()
    ssl_context = build_ssl_context(env)

    for batch_index, batch in enumerate(batches(docs, args.batch_size), start=1):
        inputs = [row["content"] for row in batch]
        try:
            vectors = call_embeddings(url, api_key, inputs, args.max_retries, args.retry_sleep_seconds, ssl_context)
        except Exception as exc:
            failed_batches.append({
                "batch_index": batch_index,
                "ids": [row["id"] for row in batch],
                "error": str(exc),
            })
            continue
        if len(vectors) != len(batch):
            failed_batches.append({
                "batch_index": batch_index,
                "ids": [row["id"] for row in batch],
                "error": f"Expected {len(batch)} vectors, received {len(vectors)}",
            })
            continue
        for row, vector in zip(batch, vectors):
            item = dict(row)
            item["content_vector"] = vector
            item["embedding_deployment"] = deployment
            item["embedding_generated_at"] = now_iso()
            vectorized.append(item)

    validation = validate_vectors(vectorized, expected_dimensions)
    status = "READY_FOR_AZURE_INDEX_UPLOAD" if validation["all_vectors_valid"] and not failed_batches and len(vectorized) == len(docs) else "NEEDS_REVIEW"

    write_jsonl(output_jsonl, vectorized)
    write_json(output_batch, {"value": vectorized})

    manifest = {
        "manifest_version": "embedding_manifest_v1",
        "generated_at": now_iso(),
        "started_at": started,
        "status": status,
        "source_documents": str(input_path),
        "output_jsonl": str(output_jsonl),
        "output_batch_json": str(output_batch),
        "embedding_endpoint_host": endpoint,
        "embedding_api_version": api_version,
        "embedding_deployment": deployment,
        "embedding_dimensions": expected_dimensions,
        "batch_size": args.batch_size,
        "counts": {
            "input_documents": len(docs),
            "vectorized_documents": len(vectorized),
            "failed_batches": len(failed_batches),
            "failed_documents": sum(len(item["ids"]) for item in failed_batches),
        },
        "validation": validation,
        "failed_batches": failed_batches,
    }
    write_json(manifest_path, manifest)
    write_report(report_path, manifest)

    print(json.dumps({
        "status": status,
        "counts": manifest["counts"],
        "validation": validation,
        "failed_batches": failed_batches,
        "outputs": {
            "jsonl": str(output_jsonl),
            "batch_json": str(output_batch),
            "manifest": str(manifest_path),
            "report": str(report_path),
        },
    }, indent=2))
    return 0 if status == "READY_FOR_AZURE_INDEX_UPLOAD" else 1


if __name__ == "__main__":
    raise SystemExit(main())
