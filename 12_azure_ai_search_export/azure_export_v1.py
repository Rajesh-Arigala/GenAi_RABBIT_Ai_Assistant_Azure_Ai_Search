#!/usr/bin/env python3
"""Prepare approved V4 chunks for Azure AI Search.

This step creates a vector-ready schema and upload-shaped documents. It does
not generate embeddings. Embedding generation and actual Azure upload are
separate later steps.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path(__file__).resolve().with_name("azure_export_config.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


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


def resolve_config_path(config_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve()


def azure_key(value: str) -> str:
    """Keep the key stable while avoiding characters Azure keys dislike."""
    return re.sub(r"[^A-Za-z0-9_=-]", "_", value)


def as_collection(value: Any) -> list[str]:
    if not value:
        return []
    return [str(item) for item in value]


def build_schema(config: dict[str, Any]) -> dict[str, Any]:
    vector = config["vector_search"]
    embedding = config["embedding"]
    semantic = config["semantic_search"]
    vector_field = embedding["vector_field_name"]

    return {
        "name": config["index_name"],
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "searchable": False, "filterable": True, "retrievable": True},
            {"name": "chunk_id", "type": "Edm.String", "searchable": False, "filterable": True, "retrievable": True},
            {"name": "document_id", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "document_version", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "page_id", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "section_id", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "parent_page_id", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "depth", "type": "Edm.Int32", "filterable": True, "sortable": True, "facetable": True, "retrievable": True},
            {"name": "title", "type": "Edm.String", "searchable": True, "filterable": False, "sortable": True, "retrievable": True},
            {"name": "source_url", "type": "Edm.String", "searchable": False, "filterable": True, "retrievable": True},
            {"name": "content", "type": "Edm.String", "searchable": True, "retrievable": True},
            {"name": "chunk_index", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "chunk_total", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "word_count", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "char_count", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "token_estimate", "type": "Edm.Int32", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "related_page_ids", "type": "Collection(Edm.String)", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "related_urls", "type": "Collection(Edm.String)", "searchable": False, "filterable": True, "retrievable": True},
            {"name": "related_relationship_types", "type": "Collection(Edm.String)", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "chunking_version", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "review_status", "type": "Edm.String", "searchable": False, "filterable": True, "facetable": True, "retrievable": True},
            {"name": "source_document_hash_sha256", "type": "Edm.String", "searchable": False, "filterable": True, "retrievable": True},
            {"name": "content_hash_sha256", "type": "Edm.String", "searchable": False, "filterable": True, "retrievable": True},
            {"name": "created_at", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True, "retrievable": True},
            {"name": "updated_at", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True, "retrievable": True},
            {
                "name": vector_field,
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "retrievable": False,
                "dimensions": embedding["dimensions"],
                "vectorSearchProfile": vector["profile_name"]
            }
        ],
        "vectorSearch": {
            "algorithms": [
                {
                    "name": vector["algorithm_name"],
                    "kind": vector["kind"],
                    "hnswParameters": {
                        "m": vector["m"],
                        "efConstruction": vector["efConstruction"],
                        "efSearch": vector["efSearch"],
                        "metric": vector["metric"]
                    }
                }
            ],
            "profiles": [
                {
                    "name": vector["profile_name"],
                    "algorithm": vector["algorithm_name"]
                }
            ]
        },
        "semantic": {
            "configurations": [
                {
                    "name": semantic["configuration_name"],
                    "prioritizedFields": {
                        "titleField": {"fieldName": semantic["title_field"]},
                        "prioritizedContentFields": [{"fieldName": f} for f in semantic["content_fields"]],
                        "prioritizedKeywordsFields": [{"fieldName": f} for f in semantic["keyword_fields"]]
                    }
                }
            ]
        }
    }


def build_azure_document(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "@search.action": "upload",
        "id": azure_key(chunk["id"]),
        "chunk_id": chunk["chunk_id"],
        "document_id": chunk["document_id"],
        "document_version": int(chunk["document_version"]),
        "page_id": chunk["page_id"],
        "section_id": chunk["section_id"],
        "parent_page_id": chunk["parent_page_id"],
        "depth": int(chunk["depth"]),
        "title": chunk["title"],
        "source_url": chunk["source_url"],
        "content": chunk["content"],
        "chunk_index": int(chunk["chunk_index"]),
        "chunk_total": int(chunk["chunk_total"]),
        "word_count": int(chunk["word_count"]),
        "char_count": int(chunk["char_count"]),
        "token_estimate": int(chunk["token_estimate"]),
        "related_page_ids": as_collection(chunk.get("related_page_ids")),
        "related_urls": as_collection(chunk.get("related_urls")),
        "related_relationship_types": as_collection(chunk.get("related_relationship_types")),
        "chunking_version": chunk["chunking_version"],
        "review_status": chunk["review_status"],
        "source_document_hash_sha256": chunk["source_document_hash_sha256"],
        "content_hash_sha256": chunk["content_hash_sha256"],
        "created_at": chunk["created_at"],
        "updated_at": chunk["updated_at"]
    }


def validate_export(schema: dict[str, Any], docs: list[dict[str, Any]], approved_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    field_names = {field["name"] for field in schema["fields"]}
    doc_ids = [doc["id"] for doc in docs]
    missing_required = []
    for doc in docs:
        for field in ["id", "chunk_id", "document_id", "page_id", "section_id", "title", "source_url", "content"]:
            if field not in doc or doc[field] in ("", None):
                missing_required.append({"id": doc.get("id"), "field": field})
    unknown_doc_fields = sorted({key for doc in docs for key in doc if not key.startswith("@search.") and key not in field_names})
    return {
        "approved_chunks_input": len(approved_chunks),
        "azure_documents_output": len(docs),
        "duplicate_azure_ids": len(doc_ids) - len(set(doc_ids)),
        "missing_required_fields": missing_required,
        "unknown_document_fields": unknown_doc_fields,
        "content_vector_in_documents": any("content_vector" in doc for doc in docs),
        "vector_field_in_schema": "content_vector" in field_names
    }


def write_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# Azure AI Search Export Report\n",
        f"Generated at: {manifest['generated_at']}\n\n",
        "## Status\n",
        f"- status: {manifest['status']}\n",
        f"- index_name: {manifest['index_name']}\n",
        f"- embedding_status: {manifest['embedding_status']}\n\n",
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
    lines.append("\n## Important Note\n")
    lines.append("- Upload documents do not include `content_vector` yet. Generate embeddings before vector upload.\n")
    lines.append("- The schema is vector-ready and includes HNSW configuration for the future Azure index.\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export approved chunks in Azure AI Search shape.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = load_json(config_path)
    approved_path = resolve_config_path(config_path, config["input_approved_chunks"])
    approved_manifest_path = resolve_config_path(config_path, config["input_approved_manifest"])
    output_dir = resolve_config_path(config_path, config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    approved_chunks = read_jsonl(approved_path)
    approved_manifest = load_json(approved_manifest_path)
    schema = build_schema(config)
    azure_docs = [build_azure_document(chunk) for chunk in approved_chunks]
    validation = validate_export(schema, azure_docs, approved_chunks)

    outputs = config["outputs"]
    schema_path = output_dir / outputs["index_schema"]
    jsonl_path = output_dir / outputs["upload_documents_jsonl"]
    batch_path = output_dir / outputs["upload_documents_batch_json"]
    manifest_path = output_dir / outputs["export_manifest"]
    report_path = output_dir / outputs["export_report_md"]

    write_json(schema_path, schema)
    write_jsonl(jsonl_path, azure_docs)
    write_json(batch_path, {"value": azure_docs})

    status = "READY_FOR_EMBEDDING_GENERATION"
    if validation["duplicate_azure_ids"] or validation["missing_required_fields"] or validation["unknown_document_fields"]:
        status = "NEEDS_REVIEW"

    manifest = {
        "manifest_version": "azure_export_manifest_v1",
        "generated_at": now_iso(),
        "export_version": config["export_version"],
        "index_name": config["index_name"],
        "status": status,
        "embedding_status": config["embedding"]["status"],
        "source_approved_chunks": str(approved_path),
        "source_approved_manifest": str(approved_manifest_path),
        "source_approved_status": approved_manifest.get("status"),
        "outputs": {
            "index_schema": str(schema_path),
            "upload_documents_jsonl": str(jsonl_path),
            "upload_documents_batch_json": str(batch_path),
            "export_report_md": str(report_path)
        },
        "counts": {
            "approved_chunks_input": len(approved_chunks),
            "azure_documents_output": len(azure_docs),
            "documents_represented": len({doc["document_id"] for doc in azure_docs}),
            "pages_represented": len({doc["page_id"] for doc in azure_docs}),
            "total_words": sum(doc["word_count"] for doc in azure_docs),
            "total_chars": sum(doc["char_count"] for doc in azure_docs)
        },
        "schema_summary": {
            "fields": len(schema["fields"]),
            "vector_field": config["embedding"]["vector_field_name"],
            "vector_dimensions": config["embedding"]["dimensions"],
            "vector_algorithm": config["vector_search"]["kind"],
            "hnsw": config["vector_search"]
        },
        "validation": validation
    }

    write_json(manifest_path, manifest)
    write_report(report_path, manifest)
    print(json.dumps({"status": status, "counts": manifest["counts"], "validation": validation}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
