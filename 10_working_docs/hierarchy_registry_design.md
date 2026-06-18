# Hierarchy Registry Design
This file explains `01_input_seed_and_config/hierarchy_registry.json`, the Step 1 source of truth for the dashboard-ready document lifecycle.
## What It Controls
- Every webpage/document lives in a stable hierarchy slot.
- New uploads must attach to an existing slot.
- Deleting a document removes the content but keeps the slot alive.
- Chunks and Azure index records inherit `page_id`, parent, depth, section, title, and URL from the slot.
- Replacing a document should increment the document version and mark existing chunks/index records stale.

## Registry Counts
- approved_ready_documents: 53
- registry_nodes_total: 56
- occupied_ready_slots: 53
- empty_planned_slots: 3
- synthetic_or_future_placeholders: 3

## Placeholder Notes
- `03_AI_Projects` is a visual parent slot for the approved AI project pages. It does not currently have its own RAG document.
- `04_GenAI` is a future placeholder only. It is not ready for chunking and is not part of the approved 53-document corpus.
- `02_Tech_02_MLOps` is a visual parent slot for MLOps subsections. It is not counted as an approved ready document until content is attached.

## Dashboard Behavior
- Left panel: render `nodes` as a tree using `parent_page_id` and `children`.
- Main panel: selected slot details, current document, status, version, chunk status, and indexing status.
- Upload: allowed only against a selected hierarchy node.
- Delete: set document status to `deleted_content`, clear current content reference, keep the node.
- Re-upload: attach new content to the same `page_id`, increment version, then re-chunk.

## Current Top-Level View
- 00_Homepage | occupied_ready | children: 4
- 01_Business_Skills | occupied_ready | children: 6
- 02_Tech_01_Technical_Skills | occupied_ready | children: 8
- 03_AI_Projects | empty_planned | children: 5
- 04_GenAI | empty_planned | children: 0

## Updated Workflow Notes

The hierarchy registry is the visual source of truth for the future document lifecycle dashboard. It should be read together with:

```text
10_working_docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md
10_working_docs/END_TO_END_WORKFLOW_SUMMARY.md
```

Key rule:

```text
A hierarchy slot should remain visible even when document content is deleted.
```

This makes the dashboard stable: users can see missing placeholders, re-upload to the same page_id, preserve the hierarchy, and rebuild chunks without losing the corpus structure.

