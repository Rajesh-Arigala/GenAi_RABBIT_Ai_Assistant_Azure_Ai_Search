#!/usr/bin/env python3
"""Admin lifecycle actions for V4 chunks.

This script is intentionally file-based for now. The same actions can later
be exposed as dashboard/API buttons without changing the chunk record format.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHUNK_DIR = ROOT / "09_future_output_chunks"
CHUNKS_PATH = CHUNK_DIR / "chunks_v1.jsonl"
REGISTRY_PATH = CHUNK_DIR / "chunk_registry.json"
APPROVED_PATH = CHUNK_DIR / "approved_chunks_v1.jsonl"
APPROVED_MANIFEST_PATH = CHUNK_DIR / "approved_chunks_manifest.json"
ADMIN_REPORT_PATH = CHUNK_DIR / "chunk_admin_report.md"


APPROVED = "approved"
PENDING = "pending_review"
DELETED = "deleted"
STALE = "stale"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
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


def load_state() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    chunks = read_jsonl(CHUNKS_PATH)
    registry = read_json(REGISTRY_PATH)
    return chunks, registry


def save_state(chunks: list[dict[str, Any]], registry: dict[str, Any]) -> None:
    write_jsonl(CHUNKS_PATH, chunks)
    registry["chunks"] = [{k: v for k, v in chunk.items() if k != "content"} for chunk in chunks]
    registry["updated_at"] = now_iso()
    registry["counts"] = build_counts(chunks)
    registry["validation"] = build_validation(chunks)
    write_json(REGISTRY_PATH, registry)


def build_counts(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = Counter(chunk["review_status"] for chunk in chunks)
    active_chunks = [c for c in chunks if c["review_status"] != DELETED]
    return {
        "chunks_total": len(chunks),
        "active_chunks": len(active_chunks),
        "approved_chunks": status_counts[APPROVED],
        "pending_review_chunks": status_counts[PENDING],
        "stale_chunks": status_counts[STALE],
        "deleted_chunks": status_counts[DELETED],
        "documents_represented": len({c["document_id"] for c in active_chunks}),
        "pages_represented": len({c["page_id"] for c in active_chunks}),
        "total_active_words": sum(c["word_count"] for c in active_chunks),
        "total_approved_words": sum(c["word_count"] for c in chunks if c["review_status"] == APPROVED),
    }


def build_validation(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    active = [c for c in chunks if c["review_status"] != DELETED]
    approved = [c for c in chunks if c["review_status"] == APPROVED]
    chunk_ids = [c["chunk_id"] for c in chunks]
    return {
        "duplicate_chunk_ids": len(chunk_ids) - len(set(chunk_ids)),
        "empty_active_chunks": [c["chunk_id"] for c in active if not c["content"].strip()],
        "approved_chunks_without_content": [c["chunk_id"] for c in approved if not c["content"].strip()],
        "approved_chunks_not_indexable": [
            c["chunk_id"]
            for c in approved
            if c["indexing_status"] not in {"ready_for_indexing", "not_indexed", "needs_reindex"}
        ],
    }


def print_summary(chunks: list[dict[str, Any]]) -> None:
    counts = build_counts(chunks)
    by_page = Counter(c["page_id"] for c in chunks if c["review_status"] != DELETED)
    payload = {
        "counts": counts,
        "min_chunks_per_page": min(by_page.values()) if by_page else 0,
        "max_chunks_per_page": max(by_page.values()) if by_page else 0,
        "top_pages_by_chunk_count": by_page.most_common(10),
        "validation": build_validation(chunks),
    }
    print(json.dumps(payload, indent=2))


def approve_all(chunks: list[dict[str, Any]]) -> int:
    changed = 0
    ts = now_iso()
    for chunk in chunks:
        if chunk["review_status"] in {PENDING, STALE}:
            chunk["review_status"] = APPROVED
            chunk["indexing_status"] = "ready_for_indexing"
            chunk["approved_at"] = ts
            chunk["updated_at"] = ts
            changed += 1
    return changed


def approve_page(chunks: list[dict[str, Any]], page_id: str) -> int:
    changed = 0
    ts = now_iso()
    for chunk in chunks:
        if chunk["page_id"] == page_id and chunk["review_status"] in {PENDING, STALE}:
            chunk["review_status"] = APPROVED
            chunk["indexing_status"] = "ready_for_indexing"
            chunk["approved_at"] = ts
            chunk["updated_at"] = ts
            changed += 1
    return changed


def mark_stale_page(chunks: list[dict[str, Any]], page_id: str) -> int:
    changed = 0
    ts = now_iso()
    for chunk in chunks:
        if chunk["page_id"] == page_id and chunk["review_status"] != DELETED:
            chunk["review_status"] = STALE
            chunk["indexing_status"] = "needs_reindex"
            chunk["stale_at"] = ts
            chunk["updated_at"] = ts
            changed += 1
    return changed


def delete_page(chunks: list[dict[str, Any]], page_id: str) -> int:
    changed = 0
    ts = now_iso()
    for chunk in chunks:
        if chunk["page_id"] == page_id and chunk["review_status"] != DELETED:
            chunk["review_status"] = DELETED
            chunk["indexing_status"] = "delete_from_index"
            chunk["deleted_at"] = ts
            chunk["updated_at"] = ts
            changed += 1
    return changed


def export_approved(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    approved = [chunk for chunk in chunks if chunk["review_status"] == APPROVED]
    write_jsonl(APPROVED_PATH, approved)
    manifest = {
        "manifest_version": "approved_chunks_manifest_v1",
        "generated_at": now_iso(),
        "source_chunks": str(CHUNKS_PATH),
        "approved_chunks_path": str(APPROVED_PATH),
        "status": "APPROVED_FOR_AZURE_EXPORT_PREP",
        "counts": {
            "approved_chunks": len(approved),
            "documents_represented": len({c["document_id"] for c in approved}),
            "pages_represented": len({c["page_id"] for c in approved}),
            "total_words": sum(c["word_count"] for c in approved),
            "total_chars": sum(c["char_count"] for c in approved),
            "min_chunk_words": min((c["word_count"] for c in approved), default=0),
            "max_chunk_words": max((c["word_count"] for c in approved), default=0),
        },
        "validation": build_validation(approved),
    }
    write_json(APPROVED_MANIFEST_PATH, manifest)
    write_admin_report(manifest)
    return manifest


def write_admin_report(manifest: dict[str, Any]) -> None:
    lines = [
        "# Chunk Admin Report\n",
        f"Generated at: {manifest['generated_at']}\n\n",
        "## Approved Export\n",
        f"- status: {manifest['status']}\n",
        f"- approved_chunks_path: {manifest['approved_chunks_path']}\n\n",
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
    lines.append("\n## Dashboard Mapping\n")
    lines.append("- Approve button -> `approve-page` or future single-chunk approve action.\n")
    lines.append("- Delete button -> `delete-page` now, single-chunk delete later.\n")
    lines.append("- Rebuild button -> future wrapper around `chunking_v1.py` with selected profile/scope.\n")
    lines.append("- Export button -> `export-approved`.\n")
    ADMIN_REPORT_PATH.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage V4 chunk approval lifecycle.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")
    sub.add_parser("approve-all")
    approve_page_parser = sub.add_parser("approve-page")
    approve_page_parser.add_argument("--page-id", required=True)
    stale_parser = sub.add_parser("mark-stale-page")
    stale_parser.add_argument("--page-id", required=True)
    delete_parser = sub.add_parser("delete-page")
    delete_parser.add_argument("--page-id", required=True)
    sub.add_parser("export-approved")
    args = parser.parse_args()

    chunks, registry = load_state()

    if args.command == "summary":
        print_summary(chunks)
        return 0
    if args.command == "approve-all":
        changed = approve_all(chunks)
        save_state(chunks, registry)
        print(json.dumps({"action": "approve-all", "changed_chunks": changed, "counts": build_counts(chunks)}, indent=2))
        return 0
    if args.command == "approve-page":
        changed = approve_page(chunks, args.page_id)
        save_state(chunks, registry)
        print(json.dumps({"action": "approve-page", "page_id": args.page_id, "changed_chunks": changed}, indent=2))
        return 0
    if args.command == "mark-stale-page":
        changed = mark_stale_page(chunks, args.page_id)
        save_state(chunks, registry)
        print(json.dumps({"action": "mark-stale-page", "page_id": args.page_id, "changed_chunks": changed}, indent=2))
        return 0
    if args.command == "delete-page":
        changed = delete_page(chunks, args.page_id)
        save_state(chunks, registry)
        print(json.dumps({"action": "delete-page", "page_id": args.page_id, "changed_chunks": changed}, indent=2))
        return 0
    if args.command == "export-approved":
        manifest = export_approved(chunks)
        print(json.dumps({"action": "export-approved", "manifest": manifest}, indent=2))
        return 0

    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
