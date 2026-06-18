# UI Modes, Traceability, Observability, And Logging Contract

# Project Name

```text
RABBIT Assistant
Raj AI Business and Beyond Intelligence Tech Assistant
```

Acronym mapping:

```text
RA = Raj AI
B = Business
B = Beyond
I = Intelligence
T = Tech
```


This document defines what belongs where in the future Flask UI and backend response contract for the Business-Tech RAG assistant.

The UI will have four modes:

```text
1. User Mode
2. Debug Mode
3. Observability Mode
4. Tech Mode
```

Tech Mode is a dummy placeholder for now. It will later inherit deeper technical diagnostics inspired by the earlier RAG-Raj-Ai-Assistant project, but we will not implement it fully yet.

## Core Separation Principle

```text
User Mode = clean answer experience
Debug Mode = why this answer was produced
Observability Mode = how the system performed
Tech Mode = deeper engineering internals, later
Logging = persistent machine-readable event history
Traceability = IDs and lineage across the whole request
```

## Backend Response Shape

Every `/api/chat` response should eventually follow this shape:

```json
{
  "user": {},
  "debug": {},
  "observability": {},
  "tech": {},
  "traceability": {},
  "logging": {}
}
```

The UI decides what to display based on selected mode.

---

# 1. User Mode

Purpose: clean recruiter/hiring manager/peer-facing answer.

User Mode should show only the final product.

## User Mode Fields

```text
question
answer
answer_confidence_label
answer_confidence_score
answer_confidence_reason
sources
suggested_followups
```

## User Mode Sources

Each source should show:

```text
page_id
title
source_url
section_id
chunk_index / chunk_total
```

Do not show raw scores by default in User Mode. Scores can confuse non-technical users.

## User Mode Confidence

This is LLM-side answer confidence, not retrieval score.

```text
answer_confidence_label: high | medium | low
answer_confidence_score: 0.0-1.0
answer_confidence_reason
```

Important wording:

```text
This is a qualitative LLM confidence estimate based on retrieved evidence, not a statistical probability.
```

---

# 2. Debug Mode

Purpose: explain how the answer was constructed.

Debug Mode is for interviews, demos, and development review. It answers:

```text
What did we retrieve?
Why did we retrieve it?
Which chunks grounded the answer?
What scores did retrieval produce?
What prompt/context was sent to the LLM?
```

## Debug Mode Categories

```text
A. Retrieval Debug
B. Evidence Debug
C. Prompt Debug
D. Confidence Debug
E. Source Debug
```

## A. Retrieval Debug Fields

```text
search_mode
query_text
query_embedding_generated: true/false
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
vector_score_raw
hybrid_score_raw
keyword_score_raw
```

Current note:

Azure currently returns `@search.score`. For hybrid search, this is a retrieval score, not a true probability. If Azure does not expose separate vector and keyword sub-scores, we show:

```text
retrieval_score_raw = @search.score
retrieval_score_relative_percent = score / top_score * 100
vector_score_raw = null unless separately available
keyword_score_raw = null unless separately available
hybrid_score_raw = @search.score
```

## B. Evidence Debug Fields

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

## C. Prompt Debug Fields

```text
system_prompt_name
profile_context_used: true/false
profile_context_path
retrieved_context_preview
final_prompt_preview
prompt_message_count
estimated_prompt_chars
```

## D. Confidence Debug Fields

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
Answer confidence comes from the LLM's self-assessment based on evidence.
They are different and should be displayed separately.
```

## E. Source Debug Fields

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

---

# 3. Observability Mode

Purpose: monitor system performance and operational health.

Observability Mode is not about the content of the answer. It answers:

```text
Was the system fast?
Was the system healthy?
Where was latency spent?
Which model/index/deployment was used?
Were there errors or retries?
```

## Observability Categories

```text
A. Request Metrics
B. Latency Metrics
C. Retrieval Metrics
D. LLM Metrics
E. Token/Cost Metrics
F. Reliability Metrics
G. Index/Corpus Metrics
```

## A. Request Metrics

```text
request_id
session_id
turn_id
timestamp
user_mode
search_mode
question_length_chars
question_length_words
filter_applied
top_k
```

## B. Latency Metrics

```text
embedding_latency_ms
search_latency_ms
answer_latency_ms
total_latency_ms
backend_processing_ms
client_observed_latency_ms
```

## C. Retrieval Metrics

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

## D. LLM Metrics

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
answer_confidence_label
answer_confidence_score
```

## E. Token/Cost Metrics

Current support is partial. Add when API usage is available.

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

## F. Reliability Metrics

```text
status
error_type
error_message
retry_count
timeout_flag
rate_limit_flag
ssl_error_flag
azure_search_status
azure_openai_status
```

## G. Index/Corpus Metrics

```text
index_name
index_document_count
schema_field_count
vector_dimensions
corpus_pages_count
corpus_chunks_count
chunking_version
embedding_manifest_version
azure_export_version
```

---

# 4. Tech Mode

Purpose: future deep engineering diagnostics.

For now, Tech Mode is a dummy placeholder. It should not block the UI.

## Tech Mode Placeholder Fields

```text
status: planned
message: Technical diagnostics mode will be added later.
```

## Future Tech Mode Categories

```text
A. Raw API Payloads
B. Raw Azure Search Response
C. Raw Azure OpenAI Response
D. Environment/Deployment Diagnostics
E. Schema Diagnostics
F. Chunk Lifecycle Diagnostics
G. Dashboard/Admin Action Logs
```

## Future Tech Mode Fields

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
```

Tech Mode should be owner/admin-facing only.

---

# 5. Traceability

Purpose: connect every answer back to source data, chunk lifecycle, Azure index, prompt, and model call.

Traceability should be present in every backend response, even if hidden in User Mode.

## Traceability Fields

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

## Source Lineage Fields

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

---

# 6. Logging

Purpose: persistent event trail for debugging, audit, analytics, and dashboard history.

Logging is not the same as observability display. Observability is what we show; logging is what we store.

## Log Event Types

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
feedback_submitted
mode_changed
filter_applied
```

## Log Record Fields

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

## Storage For Now

During local Flask development:

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

---

# 7. Mode-To-Field Mapping

## User Mode Shows

```text
answer
answer_confidence_label
sources
suggested_followups
```

## Debug Mode Shows

```text
retrieved_chunks
retrieval_score_raw
retrieval_score_relative_percent
hybrid_score_raw
vector_score_raw if available
keyword_score_raw if available
prompt_preview
source lineage
answer confidence details
```

## Observability Mode Shows

```text
latencies
status/errors
model/index/deployment names
token/cost estimates when available
retrieval score distribution
request/session metrics
corpus/index counts
```

## Tech Mode Shows For Now

```text
planned placeholder only
```

## Logs Store

```text
all request lifecycle events
all errors
all observability snapshots
```

---

# 8. Immediate Implementation Plan For Flask UI

## Current Build

```text
18_flask_chat_ui/
  app.py
  templates/index.html
  static/app.js
  static/styles.css
  logs/
```

## Initial API Endpoints

```text
GET /health
GET /api/config
POST /api/chat
```

## `/api/chat` Behavior

```text
1. Accept question, mode, top_k, filter.
2. Call Step 10 `answer_question()`.
3. Add request_id/session_id/turn_id.
4. Add relative retrieval scores.
5. Add placeholder Tech Mode block.
6. Write JSONL logs.
7. Return full payload.
```

## Modes In UI

```text
User
Debug
Observability
Tech - dummy for now
```

---

# 9. Open Items

```text
1. Add retry logic around chat completion timeout.
2. Ask LLM to return structured confidence fields explicitly.
3. Add true token/cost calculations if usage data is consistently returned.
4. Add separate vector vs keyword score only if Azure exposes or we run separate searches.
5. Add Tech Mode later from prior RAG-Raj-Ai-Assistant diagnostics pattern.
```

## Audience Boundary

- User Mode is the public recruiter/HR/hiring-agent facing experience. It should read like a polished assistant on Rajesh's website, with no raw internals, no confidence labels, no chunk IDs, no retrieval scores, and no full source dump.
- User Mode can show one or two clickable relevant webpage links under the answer.
- Debug Mode is for interview/demo walkthroughs where Rajesh can show how the answer was produced: confidence proxy, retrieval evidence, source links, chunk lineage, scores, and prompt preview.
- Observability Mode is for system metrics, latency, logs, status, and operational signals.
- Tech Mode remains a later deep-diagnostics layer.

## API Observability And Retry Controls

- User Mode must not expose API internals.
- Observability Mode shows API health status, HTTP health code, health latency, total calls, successful calls, failed calls, retry clicks, last chat HTTP code, last request ID, last API latency, and last API error.
- Failed chat messages show a Retry button in the chat stream so the same question can be resent without retyping.
- Debug Mode remains focused on retrieval, sources, chunks, scores, prompt preview, and answer confidence.

## Mode Placement Decision

- API metrics go to Observability Mode: health status/code, call count, retry count, last HTTP code, latency, request id, and API errors.
- Retry is available across all modes as a chat-level recovery action whenever a request fails.
- Debug Mode stays answer-quality focused: retrieval, chunks, source lineage, scores, confidence proxy, and prompt preview.
- Tech Mode is reserved for backend/API internals: endpoints, raw payload contracts, log file locations, deployment/schema diagnostics, and future deep traces.

## Stakeholder Details And Conversation Review

RABBIT may politely ask visitors for their name, profession, and position or role in their company at the beginning of a professional conversation. In User Mode, these details should not become a distracting topic and RABBIT should not overreact to them.

For Debug, Observability, and later Tech Mode, the conversation can be reviewed after the fact to understand:

- who the stakeholder said they are
- their profession or role
- their company position if provided
- what they were trying to evaluate
- which questions they asked
- where the conversation moved professionally
- which answers, links, and evidence were shown

This is useful for improving the assistant, preparing for formal interviews, and understanding stakeholder intent. It should be treated as conversation/session review, not intrusive personal profiling.

