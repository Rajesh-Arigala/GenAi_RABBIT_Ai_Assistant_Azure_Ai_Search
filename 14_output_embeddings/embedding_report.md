# Embedding Generation Report
Generated at: 2026-06-17T20:13:17.612320+00:00

## Status
- status: READY_FOR_AZURE_INDEX_UPLOAD
- embedding_deployment: text-embedding-3-small
- embedding_dimensions: 1536

## Counts
- input_documents: 142
- vectorized_documents: 142
- failed_batches: 0
- failed_documents: 0

## Validation
- documents_total: 142
- missing_vectors: 0
- wrong_dimension_vectors: 0
- empty_content_documents: 0
- expected_dimensions: 1536
- all_vectors_valid: True

## Next Step
- Step 7: create or update the Azure AI Search index using the schema from `13_output_azure_ready`.
- Step 8: upload `azure_upload_documents_with_vectors_batch_v1.json` to Azure AI Search.
