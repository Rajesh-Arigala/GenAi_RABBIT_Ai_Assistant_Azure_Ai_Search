# Chunk Admin Report
Generated at: 2026-06-17T17:56:34.445493+00:00

## Approved Export
- status: APPROVED_FOR_AZURE_EXPORT_PREP
- approved_chunks_path: /Users/jhonny001/Desktop/website-data-store/v4_site_crawler/09_future_output_chunks/approved_chunks_v1.jsonl

## Counts
- approved_chunks: 142
- documents_represented: 53
- pages_represented: 53
- total_words: 85832
- total_chars: 648813
- min_chunk_words: 161
- max_chunk_words: 861

## Validation
- duplicate_chunk_ids: 0
- empty_active_chunks: 0
- approved_chunks_without_content: 0
- approved_chunks_not_indexable: 0

## Dashboard Mapping
- Approve button -> `approve-page` or future single-chunk approve action.
- Delete button -> `delete-page` now, single-chunk delete later.
- Rebuild button -> future wrapper around `chunking_v1.py` with selected profile/scope.
- Export button -> `export-approved`.
