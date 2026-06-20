# RABBIT Assistant

**Raj AI Business and Beyond Intelligence Tech "Assistant"**

RABBIT Assistant is a Business-Tech RAG assistant built for Rajesh Arigala. It turns a personal professional website into a searchable, grounded, recruiter-facing AI assistant using website crawling, structured data extraction, chunking, embeddings, Azure AI Search, Azure OpenAI, and a Flask web interface.

The project is designed to help recruiters, HR teams, hiring managers, consultants, collaborators, and business stakeholders understand Rajesh's business-tech profile, AI/MLOps capability, project evidence, consulting fit, and role alignment.

---

## Project Snapshot

| Area | Status |
|---|---|
| Website crawler | Complete |
| Canonical RAG corpus | 53 documents |
| Approved chunks | 142 chunks |
| Embeddings | Azure OpenAI `text-embedding-3-small` |
| Vector dimensions | 1536 |
| Search platform | Azure AI Search |
| Retrieval mode | Hybrid search |
| Web app | Flask |
| Deployment target | Render |
| Lifecycle dashboard | First version implemented, guarded log-only |
| Public assistant mode | User Mode |
| Demo/admin modes | Debug, Observability, Tech, Lifecycle |

---

## What RABBIT Does

✅ Answers professional questions about Rajesh Arigala.

✅ Grounds responses in crawled website content and Azure AI Search retrieval.

✅ Shows clean recruiter-facing answers in User Mode.

✅ Supports Debug and Observability views for demo/interview inspection.

✅ Includes a document lifecycle dashboard for corpus inspection.

✅ Uses guardrails to avoid private, off-topic, salary-number, abusive, or prompt-attack conversations.

---

## Main Architecture

```text
Rajesh's Website
  ↓
Website Crawler
  ↓
Structured JSON + Clean Text + RAG Documents
  ↓
Canonical 53-Document Corpus
  ↓
Chunking Engine
  ↓
Approved 142 Chunks
  ↓
Azure OpenAI Embeddings
  ↓
Azure AI Search Index
  ↓
Hybrid Retrieval
  ↓
RAG Answer Generation
  ↓
Flask Web App
  ↓
User / Debug / Observability / Tech / Lifecycle Modes
  ↓
Future Website Chat Widget
```

---

## Sub-Architecture 1: Data Ingestion Workflow

```text
01_input_seed_and_config/
  ↓
crawler_v4_site_crawler.py
  ↓
02_output_raw_html_rendered/
  ↓
03_output_structured_json/
  ↓
04_output_clean_json/
  ↓
05_output_clean_text/
  ↓
06_output_rag_documents/
  ↓
06_output_rag_documents_ready/
  ↓
07_output_quality_reports_manifest/
```

Purpose:

- Crawl website pages.
- Preserve rendered HTML.
- Extract structured JSON.
- Produce clean text.
- Produce RAG-ready documents.
- Generate quality/readiness reports.

Canonical input for chunking:

```text
06_output_rag_documents_ready/
```

Current canonical count:

```text
53 documents
```

---

## Sub-Architecture 2: Corpus And Hierarchy Workflow

The project uses hierarchy-aware page IDs.

Examples:

```text
00_Homepage
01_Business_Skills
01_01_Business_Skill_BPCL
02_Tech_02_MLOps_01_CICD
02_Tech_02_MLOps_02_Containers_02_Kubernetes
03_01_AI_Project_MLflow_AWS_Platform
04_GenAI
```

Why this matters:

✅ Stable source IDs.

✅ Cleaner chunk metadata.

✅ Better Azure filters.

✅ Easier debugging.

✅ Future dashboard-ready document lifecycle.

Registry files:

```text
01_input_seed_and_config/hierarchy_registry.json
01_input_seed_and_config/document_registry.json
```

---

## Sub-Architecture 3: Chunking Workflow

```text
Canonical RAG Documents
  ↓
Chunking Engine
  ↓
Chunk Registry
  ↓
Approved Chunks
  ↓
Azure-Ready Export
```

Important files:

```text
11_chunking_engine/chunking_v1.py
09_future_output_chunks/chunks_v1.jsonl
09_future_output_chunks/approved_chunks_v1.jsonl
09_future_output_chunks/chunk_registry.json
```

Current approved chunk count:

```text
142
```

---

## Sub-Architecture 4: Embeddings And Azure AI Search

```text
Approved Chunks
  ↓
Azure OpenAI Embeddings
  ↓
1536-Dimensional Vectors
  ↓
Azure AI Search Index
  ↓
Keyword + Vector + Hybrid Retrieval
```

Embedding model/deployment:

```text
text-embedding-3-small
```

Vector dimensions:

```text
1536
```

Important folders:

```text
13_embedding_generation/
14_output_embeddings/
15_azure_search_upload/
```

---

## Sub-Architecture 5: RAG Answer Generation

```text
User Question
  ↓
Guardrail Checks
  ↓
Professional-Scope Check
  ↓
Azure AI Search Retrieval
  ↓
Prompt + Profile Context
  ↓
Azure OpenAI Chat Completion
  ↓
Clean User Answer + Relevant Links
```

Important files:

```text
17_answer_generation/rag_answer_v1.py
17_answer_generation/answer_prompt_template.md
10_working_docs/profile_positioning_prompt_template.md
```

Guardrails include:

- Private/personal topic avoidance
- Salary-number avoidance
- Profanity handling
- Prompt-attack refusal
- Professional-scope redirection
- Contact boundary handling
- GenAI project boundary handling

---

## Sub-Architecture 6: Flask Web App

```text
18_flask_chat_ui/
  app.py
  templates/index.html
  static/app.js
  static/styles.css
  logs/
```

Main endpoints:

```text
GET  /
GET  /health
GET  /api/config
POST /api/chat
```

Lifecycle endpoints:

```text
GET  /api/lifecycle/summary
GET  /api/lifecycle/hierarchy
GET  /api/lifecycle/documents
GET  /api/lifecycle/chunks?page_id=...
GET  /api/lifecycle/versions?page_id=...
GET  /api/lifecycle/logs
POST /api/lifecycle/action
```

---

## UI Modes

### User Mode

Public-facing recruiter/stakeholder mode.

Shows:

- clean answer
- 1-2 relevant webpage links
- no raw internals

### Debug Mode

Explains why an answer was produced.

Shows:

- retrieved chunks
- scores
- source lineage
- prompt preview
- confidence proxy

### Observability Mode

Shows runtime/system behavior.

Shows:

- API health
- latency
- status codes
- request IDs
- retry counts
- errors

### Tech Mode

Placeholder for deeper engineering diagnostics.

Future scope:

- raw payloads
- Azure schema
- deployment diagnostics
- registry diagnostics

### Lifecycle Workspace

Admin/demo control room for corpus management.

Shows:

- hierarchy tree
- document details
- chunk inspection
- versions
- lifecycle logs
- traceability
- observability

Current action mode:

```text
guarded_log_only
```

This means actions are logged but do not mutate files or Azure records yet.

---

## Local Workflow

### 1. Go To Project

```bash
cd /Users/jhonny001/Desktop/RABBIT_Assistant
```

### 2. Run Flask App

```bash
18_flask_chat_ui/.venv/bin/python 18_flask_chat_ui/app.py
```

### 3. Open Browser

```text
http://127.0.0.1:8091
```

---

## Environment Variables

Use `.env` locally and Render environment variables in production.

Example keys:

```text
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_VERSION
AZURE_OPENAI_CHAT_DEPLOYMENT
AZURE_OPENAI_EMBEDDING_DEPLOYMENT
AZURE_OPENAI_EMBEDDING_DIMENSIONS
AZURE_SEARCH_ENDPOINT
AZURE_SEARCH_API_KEY
AZURE_SEARCH_API_VERSION
AZURE_SEARCH_INDEX_NAME
FLASK_MODE_PASSWORD
```

Do not commit `.env`.

---

## Deployment Workflow

Deployment target:

```text
Render Web Service
```

Important files:

```text
requirements.txt
render.yaml
RENDER_DEPLOYMENT_CHECKLIST.md
.env.example
```

Typical GitHub/Render flow:

```bash
git status
git add .
git commit -m "Update RABBIT Assistant"
git push
```

Then redeploy from Render if auto-deploy is not enabled.

---

## Documentation Map

Start here:

```text
10_working_docs/END_TO_END_WORKFLOW_SUMMARY.md
10_working_docs/PROJECT_HANDOFF_EVOLUTION.md
```

Crawler history:

```text
10_working_docs/WEB_CRAWLING_EVOLUTION_SINGLE_PAGE.md
10_working_docs/MULTI_PAGE_CRAWLING_EVOLUTION_SUMMARY.md
10_working_docs/WEBSITE_LINK_INVENTORY_AND_VALIDATION.md
```

Lifecycle and UI contracts:

```text
10_working_docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md
10_working_docs/ui_modes_traceability_observability_contract.md
```

Prompt and memory:

```text
10_working_docs/RABBIT_PROMPT_EVOLUTION_HISTORY.md
10_working_docs/memory_and_conversation_strategy.md
10_working_docs/profile_positioning_prompt_template.md
```

---

## Current Status

✅ Website extraction complete.

✅ Canonical corpus created.

✅ Chunking completed.

✅ Embeddings generated.

✅ Azure AI Search connected.

✅ RAG answer generation working.

✅ Flask UI working.

✅ Lifecycle dashboard first version implemented.

✅ Professional-scope guardrail implemented.

✅ Visual answer markers implemented.

✅ Permanent context-aware follow-up and validated-link rendering implemented.

⚠️ Debug Mode still needs optimization.

⚠️ Observability Mode still needs optimization.

⚠️ Tech Mode is still placeholder.

⚠️ Lifecycle actions are currently log-only, not mutating.

---

## Future Roadmap

- Finish Debug Mode UI.
- Finish Observability Mode UI.
- Expand Tech Mode diagnostics.
- Make lifecycle actions executable one by one.
- Add document upload/replace/rechunk from UI.
- Add Azure sync controls.
- Add website chat widget version.
- Add MCP/tool-calling for call, email, WhatsApp, GitHub, LinkedIn, voice.
- Add recruiter demo package.

---

## One-Line Summary

RABBIT Assistant converts Rajesh Arigala's professional website into a structured, searchable, Azure-powered RAG assistant with a public recruiter-facing chat UI and an admin-grade lifecycle/debug/observability control room.
