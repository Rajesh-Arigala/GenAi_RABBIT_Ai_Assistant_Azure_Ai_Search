# UI Modes, Traceability, Observability, And Logging Contract

## Project Name

```text
RABBIT Assistant
Raj AI Business and Beyond Intelligence Tech "Assistant"
```

Acronym mapping:

```text
RA = Raj AI
B = Business
B = Beyond
I = Intelligence
T = Tech
```

## Purpose

This document defines what belongs in each web app mode for RABBIT Assistant, what the backend response should contain, and how traceability, observability, logging, and future document lifecycle management connect to the UI.

The web demo has four modes:

```text
1. User Mode
2. Debug Mode
3. Observability Mode
4. Tech Mode
```

Mobile/user-widget experience should be clean and User Mode only. The full four-mode interface is for web demo, interview walkthrough, development review, and owner/admin use.

## Core Separation Principle

```text
User Mode = clean public/stakeholder conversation
Debug Mode = why this answer was produced
Observability Mode = how the system performed
Tech Mode = deeper engineering/admin diagnostics
Logging = persistent machine-readable event history
Traceability = IDs and lineage across request, source, chunk, prompt, and model
Document Lifecycle = corpus management from hierarchy slot to Azure sync
```

## Backend Response Shape

Every `/api/chat` response should follow this shape:

```json
{
  "status": "success",
  "user": {},
  "debug": {},
  "observability": {},
  "tech": {},
  "traceability": {},
  "logging": {}
}
```

The backend can return the full payload. The UI decides what to display by mode.

## Mode Access Rules

```text
User Mode = public
Debug Mode = password/owner demo
Observability Mode = password/owner demo
Tech Mode = password/admin demo
```

User Mode must never expose:

- raw chunks
- retrieval scores
- prompt previews
- hidden instructions
- confidence scores
- API status codes
- trace IDs
- source dumps
- internal logs

## 1. User Mode

Purpose:

```text
Clean recruiter, HR, hiring manager, consultant, collaborator, and stakeholder-facing assistant.
```

User Mode should feel like a polished website/chat-widget assistant. It speaks professionally on Rajesh Arigala's behalf.

### User Mode Shows

```text
assistant answer
1-2 clickable relevant webpage links
brief context when useful
retry button only if request fails
```

### User Mode Should Not Show

```text
confidence label or score
retrieval scores
chunk IDs
raw source list
prompt preview
API metrics
session diagnostics
large source panels
```

### User Mode Answer Style

Rules:

- Keep answers concise on mobile.
- Use bullet points only when multiple points are useful.
- Avoid repeated sentences.
- Use `Context:` instead of `Why It Matters:`.
- Avoid wording like `provided context`, `indexed sources`, or `retrieved context`.
- If unsure, say: `As his Assistant, I am not sure as of now.`
- Do not over-answer simple identity questions.
- Keep conversations professional and job/business related.

### User Mode Links

Show maximum two links:

```text
Title/header
https://...
```

Links must be clickable and blue.

### User Mode Guardrails

User Mode should refuse or redirect:

- salary numbers or salary in words
- personal/private relationship questions
- protected attributes or irrelevant identity questions
- profanity/abuse
- prompt attacks and jailbreaks
- internal instruction requests
- private availability or online/offline status

Professional contact details may be provided:

```text
Phone/WhatsApp: 9880419590
Preferred call/WhatsApp timing: 9 AM to 11 PM
Email: rajesh.arigala@redlegos.com
```

Do not claim live availability.

## 2. Debug Mode

Purpose:

```text
Explain why the answer was produced.
```

Debug Mode is for interviews, demos, and development review. It helps Rajesh show the RAG mechanism behind an answer.

### Debug Mode Questions It Answers

```text
What did we retrieve?
Why did we retrieve it?
Which chunks grounded the answer?
What scores did retrieval produce?
What prompt/context was sent to the LLM?
Which sources and page IDs influenced the answer?
```

### Debug Mode Categories

```text
A. Retrieval Debug
B. Evidence Debug
C. Prompt Debug
D. Confidence Debug
E. Source Lineage Debug
F. Conversation Review
```

### A. Retrieval Debug Fields

```text
search_mode
query_text
query_embedding_generated
top_k
filter_applied
retrieved_chunk_count
retrieved_chunks
```

Each retrieved chunk should include:

```text
rank
chunk_id
page_id
section_id
parent_page_id
title
source_url
chunk_index
chunk_total
snippet
retrieval_score_raw
retrieval_score_relative_percent
hybrid_score_raw
vector_score_raw
keyword_score_raw
```

Current Azure note:

```text
Azure currently returns @search.score. For hybrid search, this is a retrieval score, not a probability. If separate vector and keyword scores are not available, show them as null and explain that Azure did not expose those sub-scores in the response.
```

### B. Evidence Debug Fields

```text
evidence_page_ids
evidence_section_ids
source_diversity_count
unique_pages_retrieved
unique_sections_retrieved
citation_coverage_ratio
answer_supported_by_chunks_flag
unsupported_claim_risk
```

### C. Prompt Debug Fields

```text
system_prompt_name
profile_context_used
profile_context_path
retrieved_context_preview
final_prompt_preview
prompt_message_count
estimated_prompt_chars
```

### D. Confidence Debug Fields

```text
retrieval_confidence_label
retrieval_confidence_reason
answer_confidence_label
answer_confidence_score
answer_confidence_reason
grounding_status
```

Important distinction:

```text
Retrieval scores come from Azure AI Search / embeddings.
Answer confidence comes from the LLM/prompt-side assessment based on evidence.
They are different and should be displayed separately.
```

### E. Source Lineage Debug Fields

```text
page_id
source_url
rag_file_name
chunk_id
content_hash_sha256
source_document_hash_sha256
chunking_version
document_version
```

### F. Conversation Review

Debug Mode can help review:

```text
stakeholder name if voluntarily provided
profession/role if voluntarily provided
company position if voluntarily provided
questions asked
professional intent inferred from the conversation
links shown
answers that may need improvement
```

This is conversation/session review, not intrusive personal profiling.

## 3. Observability Mode

Purpose:

```text
Monitor system performance, health, failures, and reliability.
```

Observability Mode is not about answer content. It is about runtime behavior.

### Observability Questions It Answers

```text
Was the API healthy?
Was the request successful?
How long did it take?
Was there a retry?
Where did the request fail?
Which deployment/index was used?
How many calls have happened in this browser session?
```

### A. API Health Metrics

```text
health_status
health_http_code
health_latency_ms
health_checked_at
azure_search_status
azure_openai_status
```

### B. Request Metrics

```text
request_id
session_id
turn_id
timestamp
ui_mode
search_mode
question_length_chars
question_length_words
filter_applied
top_k
```

### C. API Call Counters

```text
total_calls
successful_calls
failed_calls
retry_clicks
last_chat_http_code
last_request_id
last_call_at
last_error
```

### D. Latency Metrics

```text
embedding_latency_ms
search_latency_ms
answer_latency_ms
backend_processing_ms
flask_total_latency_ms
client_observed_latency_ms
```

### E. Retrieval Metrics

```text
retrieved_chunk_count
supporting_chunk_count
top_1_score
top_3_scores
average_top_3_score
min_retrieval_score
max_retrieval_score
score_spread
relative_score_distribution
source_diversity_count
empty_retrieval_flag
low_relevance_retrieval_flag
duplicate_source_count
```

### F. LLM Metrics

```text
chat_deployment
chat_model
embedding_deployment
embedding_model
temperature
max_tokens
finish_reason
answer_length_chars
answer_length_words
```

### G. Token/Cost Metrics

Current support may be partial. Add when usage data is available.

```text
input_tokens
output_tokens
total_tokens
estimated_context_tokens
estimated_system_prompt_tokens
estimated_answer_tokens
estimated_input_cost
estimated_output_cost
estimated_total_cost
```

### H. Reliability Metrics

```text
status
error_type
error_message
retry_count
timeout_flag
rate_limit_flag
ssl_error_flag
network_error_flag
```

### I. Index/Corpus Metrics

```text
index_name
index_document_count
schema_field_count
vector_dimensions
corpus_pages_count
canonical_ready_documents_count
staging_rag_documents_count
corpus_chunks_count
chunking_version
embedding_manifest_version
azure_export_version
```

Current corpus numbers:

```text
canonical_ready_documents_count = 53
staging_rag_documents_count = 73
```

## 4. Tech Mode

Purpose:

```text
Deep engineering and admin diagnostics.
```

Tech Mode can remain placeholder for now, but the contract should be clear.

### Tech Mode Current Status

```text
status: planned
message: Technical diagnostics mode will be added later.
```

### Future Tech Mode Categories

```text
A. Raw API Payloads
B. Raw Azure Search Response
C. Raw Azure OpenAI Response
D. Environment/Deployment Diagnostics
E. Schema Diagnostics
F. Chunk Lifecycle Diagnostics
G. Document Lifecycle Dashboard Diagnostics
H. Admin Action Logs
```

### Future Tech Mode Fields

```text
raw_search_request
raw_search_response
raw_embedding_request_metadata
raw_embedding_response_metadata
raw_chat_request_metadata
raw_chat_response_metadata
azure_index_schema_snapshot
schema_field_map
chunk_registry_status
document_registry_status
hierarchy_registry_status
python_runtime
flask_runtime
api_versions
environment_variable_presence_without_values
render_deployment_status
```

Tech Mode should never expose secrets.

## 5. Traceability

Purpose:

```text
Connect every answer back to source data, chunk lifecycle, Azure index, prompt, and model call.
```

Traceability should be present in every backend response but hidden from User Mode.

### Traceability Fields

```text
request_id
session_id
turn_id
question_hash
answer_hash
index_name
search_service_endpoint
chunk_ids_used
page_ids_used
section_ids_used
source_urls_used
document_ids_used
document_versions_used
chunking_version
embedding_deployment
embedding_dimensions
chat_deployment
prompt_template_version
profile_context_version
retrieval_test_suite_version
```

### Source Lineage Fields

```text
page_id
document_id
chunk_id
source_url
rag_ready_path
source_document_hash_sha256
content_hash_sha256
chunk_index
chunk_total
created_at
updated_at
```

## 6. Logging

Purpose:

```text
Persistent event trail for debugging, audit, analytics, and dashboard history.
```

Observability is what we show. Logging is what we store.

### Log Event Types

```text
chat_request_received
query_embedding_started
query_embedding_completed
azure_search_started
azure_search_completed
llm_generation_started
llm_generation_completed
answer_returned
error_occurred
retry_clicked
feedback_submitted
mode_changed
filter_applied
document_uploaded
document_replaced
document_deleted_content
chunks_rebuilt
chunks_approved
azure_export_started
azure_export_completed
azure_sync_started
azure_sync_completed
```

### Log Record Fields

```text
event_id
event_type
request_id
session_id
turn_id
timestamp
status
latency_ms
message
error_type
error_message
metadata
```

### Storage For Now

```text
18_flask_chat_ui/logs/chat_events.jsonl
18_flask_chat_ui/logs/error_events.jsonl
18_flask_chat_ui/logs/observability_events.jsonl
```

Later production options:

```text
CloudWatch
S3
Azure Monitor
Database table
OpenTelemetry collector
```

## 7. Document Lifecycle Connection

The document lifecycle dashboard is a future admin UI. It should connect to the same traceability and observability principles.

Dashboard actions:

```text
GET hierarchy
GET documents
GET chunks
POST upload document
PUT replace document
DELETE document content
POST rechunk document
POST approve chunks
POST export azure
POST sync azure
GET versions
GET logs
```

Important rule:

```text
Deleting document content keeps the hierarchy placeholder alive.
```

Document lifecycle details are defined in:

```text
10_working_docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md
```

## 8. Mode-To-Field Mapping

### User Mode Shows

```text
clean answer
1-2 relevant clickable links
retry button if failed
```

### Debug Mode Shows

```text
retrieved chunks
retrieval scores
relative retrieval scores
source lineage
prompt preview
answer confidence details
evidence coverage
conversation review signals
```

### Observability Mode Shows

```text
API health
HTTP status codes
latency
call counts
retry counts
request/session IDs
error details
model/index/deployment names
retrieval score distribution
corpus/index counts
```

### Tech Mode Shows For Now

```text
planned placeholder
future diagnostics categories
```

### Logs Store

```text
all request lifecycle events
all errors
all observability snapshots
future document lifecycle actions
```

## 9. Immediate Implementation Status

Current Flask UI location:

```text
18_flask_chat_ui/
  app.py
  templates/index.html
  static/app.js
  static/styles.css
  logs/
```

Initial endpoints:

```text
GET /health
GET /api/config
POST /api/chat
```

Current status:

- User Mode has been actively tested and refined.
- Debug Mode exists but needs final UI review and optimization.
- Observability Mode exists but needs stronger metrics presentation.
- Tech Mode is still placeholder.
- Mobile should behave like a clean User Mode / future chat-widget preview.
- Web demo should keep all four modes visible for interview/demo purposes.

## 10. Open Items

```text
1. Finish Debug Mode UI layout and fields.
2. Finish Observability Mode metrics layout.
3. Keep Tech Mode placeholder but make its planned scope clear.
4. Ensure User Mode never shows confidence, raw sources, or internals.
5. Add retry count and API health display cleanly in Observability Mode.
6. Add document lifecycle dashboard later.
7. Add tool-calling actions later through MCP or another framework.
8. Keep mobile UI clean and prepare for website chat widget.
```

## 11. Latest UI/Guardrail Implementation Notes - 2026-06-20

### Document Lifecycle Workspace

The Flask UI now has a workspace switch:

```text
Chat | Lifecycle
```

The `Lifecycle` workspace is admin/demo-facing and supports inspection of:

- ✅ corpus counts
- ✅ hierarchy nodes
- ✅ document status
- ✅ chunk status
- ✅ version metadata
- ✅ lifecycle logs
- ✅ traceability paths
- ✅ observability metadata

The lifecycle workspace should be treated as a dashboard/control-room surface, not as the public mobile widget.

### Lifecycle Observability Contract

Lifecycle API responses may include:

```json
{
  "observability": {
    "request_id": "life_req_...",
    "action": "summary_read",
    "status": "success",
    "page_id": "00_Homepage",
    "record_count": 4,
    "timestamp": "...",
    "latency_ms": 12.34,
    "mutation_mode": "guarded_log_only"
  },
  "traceability": {
    "hierarchy_registry": ".../hierarchy_registry.json",
    "document_registry": ".../document_registry.json",
    "chunk_registry": ".../chunk_registry.json",
    "approved_chunks": ".../approved_chunks_v1.jsonl",
    "lifecycle_log": ".../lifecycle_events.jsonl"
  }
}
```

### Professional-Scope Guardrail

A broad allowed-scope guardrail has been implemented before RAG retrieval:

```text
Specific safety guardrails
  ↓
Professional-scope check
  ↓
RAG retrieval only if in scope
```

Out-of-scope questions receive a polite redirect. They should not trigger Azure retrieval and should not show sources.

### Visual Answer Markers

User-facing answers may use visual markers in addition to normal bullets:

```text
✅ success / validated point
✔️ check point
☑️ selected/confirmed point
✓ concise tick
🟢 green status marker
📌 context note
🔎 evidence marker
⚠️ guardrail/boundary/uncertainty
```

These markers improve readability but should not be overused.

