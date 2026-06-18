#!/usr/bin/env python3
"""Create local, metadata-rich chunks from the V4 document registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path(__file__).resolve().with_name("chunking_config.json")


@dataclass(frozen=True)
class ChunkConfig:
    chunking_version: str
    target_words: int
    max_words: int
    overlap_words: int
    min_tail_words: int
    token_estimate_divisor: float
    only_document_statuses: set[str]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def resolve_config_path(config_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (config_path.parent / path).resolve()


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = normalize_text(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9#])", text)
    return [p.strip() for p in parts if p.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def take_overlap(sentences: list[str], overlap_words: int) -> list[str]:
    if overlap_words <= 0:
        return []
    selected: list[str] = []
    total = 0
    for sentence in reversed(sentences):
        selected.append(sentence)
        total += word_count(sentence)
        if total >= overlap_words:
            break
    return list(reversed(selected))


def split_oversized_sentence(sentence: str, max_words: int) -> list[str]:
    words = sentence.split()
    if len(words) <= max_words:
        return [sentence]
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)]


def chunk_text(text: str, cfg: ChunkConfig) -> list[str]:
    sentences: list[str] = []
    for sentence in split_sentences(text):
        sentences.extend(split_oversized_sentence(sentence, cfg.max_words))

    chunks: list[list[str]] = []
    current: list[str] = []
    current_words = 0

    for sentence in sentences:
        sentence_words = word_count(sentence)
        would_exceed_target = current_words >= cfg.target_words
        would_exceed_max = current and current_words + sentence_words > cfg.max_words
        if would_exceed_target or would_exceed_max:
            chunks.append(current)
            current = take_overlap(current, cfg.overlap_words)
            current_words = sum(word_count(s) for s in current)
        current.append(sentence)
        current_words += sentence_words

    if current:
        if chunks and current_words < cfg.min_tail_words:
            tail = current
            merged = chunks.pop()
            merged.extend(tail)
            if sum(word_count(s) for s in merged) <= cfg.max_words + cfg.min_tail_words:
                chunks.append(merged)
            else:
                chunks.append(merged)
                chunks.append(tail)
        else:
            chunks.append(current)

    return [normalize_text(" ".join(chunk)) for chunk in chunks if normalize_text(" ".join(chunk))]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_cross_refs(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {}
    refs = load_json(path)
    by_source: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        by_source.setdefault(ref["source_page_id"], []).append(ref)
    return by_source


def build_chunk_id(page_id: str, document_version: int, chunk_index: int, content: str) -> str:
    digest = sha256_text(content)[:12]
    return f"{page_id}__v{document_version}__chunk_{chunk_index:03d}__{digest}"


def build_chunks(
    documents: list[dict[str, Any]],
    hierarchy_by_page_id: dict[str, dict[str, Any]],
    refs_by_source: dict[str, list[dict[str, Any]]],
    cfg: ChunkConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    chunks: list[dict[str, Any]] = []
    document_updates: list[dict[str, Any]] = []
    created_at = datetime.now(timezone.utc).isoformat()

    for document in documents:
        if document["document_status"] not in cfg.only_document_statuses:
            continue
        content_path = Path(document["rag_ready_path"])
        text = normalize_text(content_path.read_text(encoding="utf-8", errors="replace"))
        pieces = chunk_text(text, cfg)
        page_id = document["page_id"]
        hierarchy = hierarchy_by_page_id[page_id]
        related = refs_by_source.get(page_id, [])
        related_page_ids = sorted({r["target_page_id"] for r in related})
        related_urls = sorted({r["target_url"] for r in related})
        relationship_types = sorted({r["relationship"] for r in related})

        for idx, content in enumerate(pieces, start=1):
            wc = word_count(content)
            chunk = {
                "id": build_chunk_id(page_id, document["version"], idx, content),
                "chunk_id": build_chunk_id(page_id, document["version"], idx, content),
                "document_id": document["document_id"],
                "document_version": document["version"],
                "page_id": page_id,
                "section_id": document["section_id"],
                "parent_page_id": document["parent_page_id"],
                "depth": document["depth"],
                "title": document["title"],
                "source_url": document["source_url"],
                "hierarchy_slot_status": hierarchy["slot_status"],
                "chunk_index": idx,
                "chunk_total": len(pieces),
                "content": content,
                "word_count": wc,
                "char_count": len(content),
                "token_estimate": int(wc / cfg.token_estimate_divisor),
                "content_hash_sha256": sha256_text(content),
                "source_document_hash_sha256": document["content_hash_sha256"],
                "rag_file_name": document["rag_file_name"],
                "rag_ready_path": document["rag_ready_path"],
                "related_page_ids": related_page_ids,
                "related_urls": related_urls,
                "related_relationship_types": relationship_types,
                "chunking_version": cfg.chunking_version,
                "created_at": created_at,
                "updated_at": created_at,
                "review_status": "pending_review",
                "indexing_status": "not_indexed",
            }
            chunks.append(chunk)

        updated = dict(document)
        updated["document_status"] = "chunked"
        updated["chunking_status"] = "chunked"
        updated["chunk_count"] = len(pieces)
        updated["last_chunked_at"] = created_at
        updated["updated_at"] = created_at
        document_updates.append(updated)

    return chunks, document_updates


def validate_chunks(chunks: list[dict[str, Any]], documents: list[dict[str, Any]]) -> dict[str, Any]:
    chunk_ids = [c["chunk_id"] for c in chunks]
    empty_chunks = [c["chunk_id"] for c in chunks if not c["content"].strip()]
    large_chunks = [c["chunk_id"] for c in chunks if c["word_count"] > 900]
    document_ids_with_chunks = {c["document_id"] for c in chunks}
    missing_documents = [
        d["document_id"] for d in documents if d["document_status"] in {"uploaded_ready", "chunked"} and d["document_id"] not in document_ids_with_chunks
    ]
    return {
        "total_chunks": len(chunks),
        "duplicate_chunk_ids": len(chunk_ids) - len(set(chunk_ids)),
        "empty_chunks": empty_chunks,
        "large_chunks_over_900_words": large_chunks,
        "documents_without_chunks": missing_documents,
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_report(path: Path, manifest: dict[str, Any], placeholder_slots: list[dict[str, Any]]) -> None:
    lines = [
        "# Chunk Quality Report\n",
        f"Generated at: {manifest['generated_at']}\n\n",
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
    lines.append("\n## Placeholder Slots Excluded\n")
    for slot in placeholder_slots:
        lines.append(f"- {slot['page_id']} | {slot['slot_status']} | {slot['node_type']}\n")
    lines.append("\n## Next Gate\n")
    lines.append("- Review chunk samples and validation results before Azure export.\n")
    lines.append("- Keep `review_status` as `pending_review` until we approve the chunk set.\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create chunks from V4 document registry.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to chunking config JSON.")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    raw_config = load_json(config_path)
    cfg = ChunkConfig(
        chunking_version=raw_config["chunking_version"],
        target_words=int(raw_config["target_words"]),
        max_words=int(raw_config["max_words"]),
        overlap_words=int(raw_config["overlap_words"]),
        min_tail_words=int(raw_config["min_tail_words"]),
        token_estimate_divisor=float(raw_config["token_estimate_divisor"]),
        only_document_statuses=set(raw_config["only_document_statuses"]),
    )

    document_registry_path = resolve_config_path(config_path, raw_config["input_document_registry"])
    hierarchy_registry_path = resolve_config_path(config_path, raw_config["input_hierarchy_registry"])
    cross_reference_path = resolve_config_path(config_path, raw_config["input_cross_reference_report"])
    output_dir = resolve_config_path(config_path, raw_config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    document_registry = load_json(document_registry_path)
    hierarchy_registry = load_json(hierarchy_registry_path)
    hierarchy_by_page_id = {node["page_id"]: node for node in hierarchy_registry["nodes"]}
    refs_by_source = load_cross_refs(cross_reference_path)

    chunks, updated_documents = build_chunks(
        document_registry["documents"],
        hierarchy_by_page_id,
        refs_by_source,
        cfg,
    )
    validation = validate_chunks(chunks, document_registry["documents"])

    counts = {
        "source_documents": len(document_registry["documents"]),
        "documents_chunked": len(updated_documents),
        "placeholder_slots_excluded": len(document_registry["placeholder_slots"]),
        "chunks_total": len(chunks),
        "total_chunk_words": sum(c["word_count"] for c in chunks),
        "total_chunk_chars": sum(c["char_count"] for c in chunks),
        "average_chunk_words": round(sum(c["word_count"] for c in chunks) / len(chunks), 2) if chunks else 0,
        "min_chunk_words": min((c["word_count"] for c in chunks), default=0),
        "max_chunk_words": max((c["word_count"] for c in chunks), default=0),
    }

    generated_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "manifest_version": "chunks_v1_manifest",
        "generated_at": generated_at,
        "chunking_version": cfg.chunking_version,
        "source_document_registry": str(document_registry_path),
        "source_hierarchy_registry": str(hierarchy_registry_path),
        "source_cross_reference_report": str(cross_reference_path),
        "outputs": {},
        "config": {
            "target_words": cfg.target_words,
            "max_words": cfg.max_words,
            "overlap_words": cfg.overlap_words,
            "min_tail_words": cfg.min_tail_words,
        },
        "counts": counts,
        "validation": validation,
        "status": "READY_FOR_REVIEW" if not validation["empty_chunks"] and not validation["documents_without_chunks"] and validation["duplicate_chunk_ids"] == 0 else "NEEDS_REVIEW",
    }

    chunk_registry = {
        "registry_version": "chunk_registry_v1",
        "generated_at": generated_at,
        "chunking_version": cfg.chunking_version,
        "source_document_registry": str(document_registry_path),
        "document_updates": updated_documents,
        "chunks": [
            {key: value for key, value in chunk.items() if key != "content"}
            for chunk in chunks
        ],
        "counts": counts,
        "validation": validation,
    }

    outputs = raw_config["outputs"]
    chunks_jsonl = output_dir / outputs["chunks_jsonl"]
    registry_path = output_dir / outputs["chunk_registry"]
    manifest_path = output_dir / outputs["chunk_manifest"]
    report_path = output_dir / outputs["quality_report_md"]

    write_jsonl(chunks_jsonl, chunks)
    write_json(registry_path, chunk_registry)
    manifest["outputs"] = {
        "chunks_jsonl": str(chunks_jsonl),
        "chunk_registry": str(registry_path),
        "chunk_manifest": str(manifest_path),
        "quality_report_md": str(report_path),
    }
    write_json(manifest_path, manifest)
    write_report(report_path, manifest, document_registry["placeholder_slots"])

    print(json.dumps({"status": manifest["status"], "counts": counts, "validation": validation}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
