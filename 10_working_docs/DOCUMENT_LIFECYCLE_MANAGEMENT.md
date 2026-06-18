# Document Lifecycle Management

## Purpose

This document defines the complete document lifecycle management design for RABBIT Assistant. It is the admin/dashboard contract for managing documents from webpage extraction through chunking, approval, Azure AI Search export, and later re-upload or replacement.

The goal is simple: every document must live in a stable hierarchy slot, every content change must be traceable, and every chunk/index record must be rebuildable without losing the visual structure of the corpus.

## Current Corpus State

Canonical approved corpus:

```text
53 RAG-ready documents
```

Canonical ready folder:

```text
06_output_rag_documents_ready/
```

Broader staging/output folder currently contains:

```text
73 RAG document files
```

Important distinction:

- `06_output_rag_documents_ready/` is the approved canonical corpus for chunking and Azure AI Search.
- `06_output_rag_documents/` may contain extra, older, duplicate, stale, or staging files.
- Dashboard actions should operate against the canonical registry, not blindly against every file in the staging folder.

## Core Principle

```text
Hierarchy slot stays alive even when document content is deleted.
```

This means deleting a document should not remove its place in the visual tree. The placeholder remains available so the same page/document can be restored later.

## Main Registries

### Hierarchy Registry

Path:

```text
01_input_seed_and_config/hierarchy_registry.json
```

Purpose:

- Defines the visual/document tree.
- Owns stable `page_id`, `parent_page_id`, `depth`, `section_id`, title, and URL relationships.
- Keeps placeholders alive even when content is missing.
- Controls where future uploads are allowed.

### Document Registry

Path:

```text
01_input_seed_and_config/document_registry.json
```

Purpose:

- Records the current document attached to each hierarchy slot.
- Tracks file paths, status, version, hash, source URL, and readiness.
- Separates occupied slots from empty placeholders.
- Supports replace, delete-content, re-upload, re-chunk, and export operations.

## Lifecycle Statuses

Recommended document statuses:

```text
empty_planned
uploaded_raw
extracted
rag_ready
chunked_pending_review
chunks_approved
chunks_rejected
stale_after_document_change
export_ready
synced_to_azure
deleted_content
archived
error
```

Recommended chunk statuses:

```text
pending_review
approved
rejected
stale
exported
synced_to_azure
```

## Dashboard Operations

### 1. View Hierarchy

Dashboard should render a tree from `hierarchy_registry.json`.

Each node should show:

```text
page_id
title
section_id
parent_page_id
depth
source_url
slot_status
document_status
chunk_status
azure_sync_status
```

### 2. Upload Document

Upload must start from a selected hierarchy slot.

Rules:

- User selects a hierarchy node first.
- Upload attaches content to that `page_id`.
- If slot was empty, create document record version `1`.
- If slot already had content, this should be treated as replace/update.
- Compute content hash.
- Mark chunk status as `not_chunked` or `stale_after_document_change`.

### 3. Replace Document

Replacement keeps the same hierarchy slot and `page_id`.

Rules:

- Increment `document_version`.
- Store new file path and new hash.
- Preserve old document metadata in version history.
- Mark existing chunks as `stale`.
- Mark Azure index records as needing refresh.

### 4. Delete Document Content

Delete means remove active content, not remove the slot.

Rules:

- Set document status to `deleted_content`.
- Keep hierarchy node visible.
- Keep page_id reserved.
- Hide or mark chunks stale/rejected.
- Mark Azure records for deletion or deactivation.
- Keep version history.

### 5. Re-upload Into Placeholder

Rules:

- User selects the same placeholder slot.
- New content is attached to the old `page_id`.
- Increment version.
- Rebuild chunks.
- Re-run approval.
- Re-export/re-sync to Azure.

### 6. Rechunk Document

Rechunking should be document-specific.

Inputs:

```text
page_id or document_id
chunk_size
chunk_overlap
split_strategy
minimum_chunk_chars
maximum_chunk_chars
```

Rules:

- Default parameters should be available.
- User may override chunk size/overlap when needed.
- Rechunking creates a new `chunking_version`.
- Old chunks become stale unless explicitly archived.
- New chunks start as `pending_review`.

### 7. Approve Chunks

Rules:

- User can approve all chunks for now.
- Later dashboard should allow chunk-level approval.
- Only approved chunks should be exported to Azure-ready payloads.

### 8. Delete Or Reject Chunks

Rules:

- Rejecting a chunk removes it from export eligibility.
- Deleting should be soft-delete by default.
- Keep audit history of who/when/why if user identity is later added.

### 9. Export Azure

Export creates Azure-ready JSON documents from approved chunks.

Rules:

- Export only `approved` chunks.
- Include vector field only after embeddings are generated.
- Include metadata fields for filter/search/debug.
- Write export report.

### 10. Sync Azure

Sync pushes approved/exported chunks to Azure AI Search.

Rules:

- Track Azure document IDs.
- Track sync status per chunk/document.
- Track failures and retry attempts.
- Allow re-sync for one document or the whole corpus.

## Required Dashboard Views

### A. Hierarchy View

Left-side tree showing all slots, including placeholders.

### B. Document Detail View

Selected node detail:

```text
page_id
title
url
status
version
file path
word count
char count
hash
last updated
chunk count
approved chunk count
azure sync status
```

### C. Chunk Review View

Shows chunks for the selected document:

```text
chunk_id
chunk_index
chunk_total
content preview
status
score/quality flags
approve/delete/rebuild actions
```

### D. Version History View

Shows each document version:

```text
document_version
content_hash
created_at
source_file
chunking_version
azure_export_version
status
```

### E. Sync/Export View

Shows:

```text
export batch id
azure index name
records exported
records synced
failed records
retry count
last sync time
```

## Metadata Required For Each Document

```text
document_id
page_id
section_id
parent_page_id
depth
title
source_url
rag_ready_path
clean_text_path
structured_json_path
document_version
content_hash_sha256
word_count
char_count
status
created_at
updated_at
```

## Metadata Required For Each Chunk

```text
chunk_id
document_id
page_id
section_id
parent_page_id
depth
title
source_url
chunk_index
chunk_total
chunk_text
chunk_hash_sha256
chunking_version
document_version
approval_status
azure_sync_status
created_at
updated_at
```

## Azure Export Fields

Recommended Azure AI Search fields:

```text
id
content
content_vector
title
source_url
page_id
section_id
parent_page_id
depth
chunk_id
chunk_index
chunk_total
document_id
document_version
chunking_version
approval_status
created_at
updated_at
```

## Rules For The Current Project

- Use the 53 approved documents as the canonical corpus.
- Keep 04_GenAI as a placeholder until real pages are added.
- Keep visual parent slots such as `03_AI_Projects` and `02_Tech_02_MLOps` even if they do not have separate RAG documents.
- Do not mix staging/legacy files with approved ready documents during chunking.
- The dashboard must make missing or placeholder documents visible, not invisible.

## Future Enhancements

- User login for admin actions.
- Audit log per document action.
- Diff view between document versions.
- Chunk quality scoring.
- Embedding drift checks.
- Azure index delete/deactivate support.
- S3 backup of raw/clean/RAG artifacts.
- One-click rebuild for selected hierarchy branch.
