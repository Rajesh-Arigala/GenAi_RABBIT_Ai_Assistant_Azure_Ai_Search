# Document Registry Design
This file explains `01_input_seed_and_config/document_registry.json`, the Step 2 source of truth for documents attached to hierarchy slots.

## Relationship To Hierarchy
- `hierarchy_registry.json` defines the slots.
- `document_registry.json` records the current document attached to each occupied slot.
- Placeholder slots remain listed separately and are not chunkable.
- Future dashboard uploads must select a hierarchy slot first, then create or replace the document record.

## Counts
- documents_total: 53
- uploaded_ready_documents: 53
- placeholder_slots_without_documents: 3
- missing_files: 0
- total_file_size_bytes: 532792
- total_words: 69965
- total_chars: 529196

## Placeholder Slots
- 02_Tech_02_MLOps | empty_planned | section_placeholder
- 03_AI_Projects | empty_planned | section_placeholder
- 04_GenAI | empty_planned | future_section_placeholder

## Lifecycle Operations Supported Later
- Create/upload document into an empty or occupied slot.
- Read document metadata and content path.
- Update/replace document and increment version.
- Delete document content while keeping hierarchy slot alive.
- Mark chunks stale when content hash changes.
- Export only approved/chunked documents to Azure-ready format.

## Updated Handoff Notes

The complete lifecycle contract is now documented in:

```text
10_working_docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md
```

The document registry should be treated as the operational record for the canonical corpus, not merely a file list. It should drive later dashboard actions such as upload, replace, delete content, re-upload, rechunk, approve chunks, export Azure, sync Azure, and version review.

Current corpus distinction:

```text
canonical_ready_documents = 53
staging_rag_document_files = 73
```

Dashboard and chunking workflows should use the canonical ready set unless a user explicitly promotes a staging file into the registry.

