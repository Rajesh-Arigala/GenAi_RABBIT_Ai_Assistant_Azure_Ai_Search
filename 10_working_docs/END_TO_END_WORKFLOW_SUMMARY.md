# RABBIT Assistant - End-To-End Workflow Summary

## Purpose

This document summarizes the complete RABBIT Assistant workflow from website content extraction to the final recruiter-facing AI assistant experience.

It is intended as a clean project workflow handoff document. If the project is renamed, moved, redeployed, or revisited later, this document should explain the full system flow at a high level.

## Project Goal

Build a professional Business-Tech RAG assistant for Rajesh Arigala.

RABBIT Assistant should help recruiters, HR teams, hiring managers, consultants, collaborators, and business stakeholders understand Rajesh's business-tech profile, AI/MLOps work, projects, consulting fit, role fit, and professional story.

RABBIT stands for:

```text
Raj AI Business and Beyond Intelligence Tech "Assistant"
```

## High-Level Workflow

```text
Rajesh's Website
  ↓
Crawler Evolution
  ↓
V4 Multi-Page Website Extraction
  ↓
Clean Text + RAG Documents
  ↓
Quality Reports + Corpus Manifest
  ↓
Canonical 53-Document Corpus
  ↓
Chunking
  ↓
Embeddings
  ↓
Azure AI Search Index
  ↓
RAG Answer Generation
  ↓
Flask Web App
  ↓
User / Debug / Observability / Tech Modes
  ↓
Future Website Chat Widget
```

---

# 1. Website Content Source

Primary source:

```text
https://rajesharigala.com
```

The website contains Rajesh's professional content across:

- Homepage
- Business skills
- Technical skills
- MLOps pages
- AI project pages
- Future GenAI placeholder section

The website is the source of truth for the RAG corpus.

---

# 2. Single-Page Crawler Evolution

The project started by validating extraction quality on one page, mainly the homepage.

Crawler versions evolved as follows:

```text
crawler_v0.py
  ↓
crawler_playwright.py
  ↓
crawler_playwright_v2.py
  ↓
crawler_v3.py
```

## V0 - Static Crawler

Technology:

```text
requests
BeautifulSoup
ftfy
```

Role:

- Fast static fallback.
- Useful for simple pages.
- Did not execute JavaScript.

Limitation:

- Missed rendered/dynamic content.
- Not sufficient for modern website extraction.

## First Playwright Version

Technology:

```text
Playwright
BeautifulSoup
ftfy
```

Role:

- Rendered JavaScript-driven webpage content.
- Improved heading, paragraph, and KPI capture.

Limitation:

- Had hardcoded KPI patching, which created data-integrity risk.

## V2 - High Recall Debug Version

Role:

- Captured rendered content and KPI/counter candidates.
- Useful for debugging missing dynamic content.

Limitation:

- Generated very noisy RAG output.
- Too much duplicate/container text.

## V3 - Approved Single-Page Baseline

Role:

- Clean Playwright-rendered extraction.
- No hardcoded KPI patches.
- Good RAG-ready output.

Practical accuracy:

```text
90-95% clean/RAG-usable extraction for the homepage
```

Decision:

```text
crawler_v3.py became the approved single-page extraction baseline.
```

---

# 3. Multi-Page V4 Crawler

After the homepage crawler was validated, the project moved to controlled multi-page website extraction.

V4 was isolated in its own execution folder to avoid mixing with older one-page experiments.

Original V4 folder:

```text
/Users/jhonny001/Desktop/website-data-store/v4_site_crawler
```

Standalone project folder:

```text
/Users/jhonny001/Desktop/RABBIT_Assistant
```

## V4 Folder Flow

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

Supporting folders:

```text
08_output_logs/
09_future_output_chunks/
10_working_docs/
13_output_azure_ready/
14_output_embeddings/
16_retrieval_testing/
17_answer_generation/
18_flask_chat_ui/
```

---

# 4. Hierarchy And Naming

A hierarchy-aware naming system was introduced so every page has a stable identity.

Examples:

```text
00_Homepage
01_Business_Skills
01_01_Business_Skill_BPCL
01_02_Business_Skill_Medtronic
02_Tech_01_Technical_Skills
02_Tech_02_MLOps_01_CICD
02_Tech_02_MLOps_02_Containers_01_Dockers
02_Tech_02_MLOps_02_Containers_02_Kubernetes
03_01_AI_Project_MLflow_AWS_Platform
04_GenAI
```

Why this matters:

- File names show hierarchy.
- Page IDs remain stable.
- Chunks can inherit page metadata.
- Azure AI Search records can be filtered by page/section/depth.
- Future dashboard can visually show the content tree.

---

# 5. Canonical Corpus

The approved canonical corpus contains:

```text
53 RAG-ready documents
```

Canonical folder:

```text
06_output_rag_documents_ready/
```

There is also a broader staging folder:

```text
06_output_rag_documents/
```

Observed staging count:

```text
73 RAG document files
```

Important rule:

```text
Use the 53 files in 06_output_rag_documents_ready/ for chunking and Azure AI Search.
Do not blindly use every file in 06_output_rag_documents/.
```

---

# 6. Corpus Readiness

The final corpus manifest confirms the approved extraction state.

Manifest:

```text
07_output_quality_reports_manifest/V4_Final_Corpus_Manifest.md
```

Status:

```text
READY_FOR_CHUNKING_PREP
```

Final corpus totals:

```text
sections: 8
expected_pages: 53
ready_pages: 53
unique_ready_pages: 53
total_rag_words: 69,965
total_rag_bytes: 532,792
suspicious_values_count: 0
bad_encoding_pages_count: 0
```

Section readiness:

| Section | Ready Pages |
|---|---:|
| 00_Homepage | 1 |
| 01_Business_Skills | 7 |
| 02_Tech_01_Technical_Skills | 8 |
| 02_Tech_02_MLOps_01_CICD | 6 |
| 02_Tech_02_MLOps_02_Containers | 9 |
| 02_Tech_02_MLOps_03_MLOps_ML_Systems | 2 |
| 02_Tech_02_MLOps_04_IaC | 3 |
| 03_AI_Projects | 17 |

---

# 7. Cross-Reference Metadata

Some pages are related across hierarchy sections.

Example:

- MLOps ML Systems pages may link to AI project pages.
- IaC pages may connect to AWS/GCP/Azure AI project detail pages.
- CI/CD pages may connect to individual CI/CD project pages.

Cross-reference report:

```text
07_output_quality_reports_manifest/V4_Cross_Reference_Report.md
```

Decision:

```text
Use cross-reference data as metadata during chunking/retrieval.
Do not duplicate the same content under multiple parent pages.
```

---

# 8. Document Lifecycle Management

The future dashboard should manage the corpus through a stable hierarchy.

Core rule:

```text
Deleting a document removes content, but keeps the hierarchy placeholder alive.
```

Lifecycle:

```text
Hierarchy Slot
  ↓
Upload Document
  ↓
Extract / Clean / RAG-Ready
  ↓
Chunk Document
  ↓
Approve Chunks
  ↓
Export Azure Payload
  ↓
Sync Azure AI Search
  ↓
Replace / Delete / Rebuild When Needed
```

Dashboard operations planned:

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

Detailed contract:

```text
10_working_docs/DOCUMENT_LIFECYCLE_MANAGEMENT.md
```

---

# 9. Chunking

Chunking converts approved RAG documents into smaller searchable records.

Input:

```text
06_output_rag_documents_ready/
```

Output:

```text
09_future_output_chunks/
```

Chunk lifecycle:

```text
pending_review
  ↓
approved
  ↓
exported
  ↓
synced_to_azure
```

If a document changes:

```text
old chunks become stale
new chunks are rebuilt
approval happens again
Azure index is updated
```

---

# 10. Embeddings

Approved chunks are embedded before Azure upload.

Current embedding setup:

```text
Azure OpenAI
text-embedding-3-small
1536 dimensions
```

Embedding artifacts:

```text
14_output_embeddings/
```

Purpose:

- Convert chunk text into vector representations.
- Enable vector and hybrid search in Azure AI Search.

---

# 11. Azure AI Search

Azure AI Search stores searchable chunk records.

Search options:

```text
keyword search
vector search
hybrid search
metadata filtering
```

RABBIT currently favors:

```text
hybrid retrieval
```

Why:

- Keyword search helps with exact terms like BPCL, Kubernetes, CI/CD.
- Vector search helps with semantic questions.
- Hybrid search gives stronger retrieval for recruiter-style questions.

---

# 12. Answer Generation

Answer generation uses retrieved chunks plus prompt instructions.

Flow:

```text
User Question
  ↓
Azure AI Search Retrieval
  ↓
Relevant Chunks
  ↓
Prompt Template + Profile Context
  ↓
Azure OpenAI Chat Model
  ↓
RABBIT Answer
  ↓
Relevant Links
```

Answer generation folder:

```text
17_answer_generation/
```

Important files:

```text
rag_answer_v1.py
answer_prompt_template.md
```

---

# 13. RABBIT Prompt And Guardrails

RABBIT speaks on behalf of Rajesh Arigala for professional and job-related conversations.

It should focus on:

- Business leadership
- AI/analytics capability
- MLOps projects
- Role fit
- Consulting fit
- Professional transition story
- Evidence through projects and website links

Guardrails:

- No salary numbers or salary in words.
- No personal/private relationship questions.
- No protected attribute discussion.
- No profanity or abuse.
- No prompt attacks or jailbreaks.
- No hidden prompt/internal instruction disclosure.
- If unsure: `As his Assistant, I am not sure as of now.`

Prompt evolution history:

```text
10_working_docs/RABBIT_PROMPT_EVOLUTION_HISTORY.md
```

---

# 14. Flask Web App

The web app is the user-facing and demo-facing layer.

Folder:

```text
18_flask_chat_ui/
```

Main files:

```text
app.py
templates/index.html
static/app.js
static/styles.css
```

Endpoints:

```text
GET /health
GET /api/config
POST /api/chat
```

---

# 15. UI Modes

The web demo has four modes:

```text
User Mode
Debug Mode
Observability Mode
Tech Mode
```

## User Mode

Purpose:

```text
Clean public/recruiter/stakeholder conversation.
```

Shows:

- polished answer
- one or two relevant webpage links
- no technical internals

## Debug Mode

Purpose:

```text
Explain why the answer was produced.
```

Shows:

- retrieved chunks
- retrieval scores
- source lineage
- prompt preview
- confidence proxy
- evidence trail

Status:

```text
Present, but still needs final review and optimization.
```

## Observability Mode

Purpose:

```text
Show system health and runtime metrics.
```

Shows:

- API health
- status codes
- latency
- call count
- retry count
- request/session IDs
- errors
- model/index names

Status:

```text
Present, but still needs final review and optimization.
```

## Tech Mode

Purpose:

```text
Future deep diagnostics.
```

Will later show:

- raw API payloads
- Azure schema
- deployment diagnostics
- registry diagnostics
- admin/developer internals

Status:

```text
Placeholder for now.
```

Mode contract:

```text
10_working_docs/ui_modes_traceability_observability_contract.md
```

---

# 16. Mobile And Chat Widget Direction

Mobile should behave differently from the full web demo.

Mobile direction:

```text
clean
minimal
User Mode only
chat-first
no mode clutter
future website widget style
```

Final goal:

```text
Embed RABBIT as a chat widget on Rajesh's website.
```

The web app remains useful for demo/interview/debug. The website widget becomes the public assistant.

---

# 17. Future Tool Calling

Future tool/action icons are planned for:

```text
WhatsApp / Call
FaceTime
Voice / Speak
Email
Review
GitHub
LinkedIn
```

These are placeholders for later.

Possible future implementation:

```text
MCP
function/tool calling
external APIs
voice services
```

---

# 18. Deployment

Current deployment direction:

```text
Render web service
```

Render uses environment variables for:

- Azure OpenAI endpoint/key/deployment
- Azure AI Search endpoint/key/index
- Flask mode password

Deployment notes:

```text
RENDER_DEPLOYMENT_CHECKLIST.md
render.yaml
requirements.txt
.env.example
```

Local `.env` should not be committed.

---

# 19. Current Pending Work

Immediate pending items:

1. Finish Debug Mode UI and output layout.
2. Finish Observability Mode metrics layout.
3. Keep Tech Mode as clean placeholder, then expand later.
4. Continue mobile UI cleanup for chat-widget direction.
5. Build document lifecycle dashboard later.
6. Add tool-calling later.
7. Keep documentation updated after each major change.

---

# 20. Project Identity Summary

RABBIT is both:

1. A professional assistant that speaks on behalf of Rajesh Arigala.
2. Visible evidence of Rajesh's Business-AI-GenAI product-building capability.

It combines:

```text
Website data extraction
RAG corpus creation
Azure AI Search
Azure OpenAI
text embeddings
1536-dimensional vectors
hybrid retrieval
Flask web app
prompt engineering
guardrails
future chat widget design
```

The full system demonstrates how business positioning, AI retrieval, cloud search, prompt design, and product UX can work together as one stakeholder-facing assistant.

---

# 21. Latest Implementation Sync - 2026-06-20

This section records the latest code state after the workflow documentation was created.

## Implemented Since The Previous Documentation Pass

✅ **Document Lifecycle UI added**

A new `Lifecycle` workspace was added to the Flask web app beside the existing chat workspace.

Implemented UI areas:

- ✅ Corpus summary cards
- ✅ Hierarchy tree
- ✅ Selected document detail view
- ✅ Chunk inspection tab
- ✅ Version/status tab
- ✅ Lifecycle logs tab
- ✅ Trace/observability tab
- ✅ Guarded lifecycle action buttons

✅ **Lifecycle backend APIs added**

Implemented endpoints:

```text
GET  /api/lifecycle/summary
GET  /api/lifecycle/hierarchy
GET  /api/lifecycle/documents
GET  /api/lifecycle/chunks?page_id=...
GET  /api/lifecycle/versions?page_id=...
GET  /api/lifecycle/logs
POST /api/lifecycle/action
```

✅ **Lifecycle tracing, observability, and logging added**

Lifecycle responses now include:

- ✅ request ID
- ✅ timestamp
- ✅ page ID
- ✅ action name
- ✅ latency
- ✅ registry paths
- ✅ mutation mode
- ✅ before-state snapshot
- ✅ after-state placeholder
- ✅ event log path

Lifecycle log file:

```text
18_flask_chat_ui/logs/lifecycle_events.jsonl
```

Current mutation mode:

```text
guarded_log_only
```

This means lifecycle buttons log the admin intent but do not yet mutate files, chunks, or Azure AI Search records.

✅ **Professional-scope guardrail added**

RABBIT now uses an allowed-scope guardrail before retrieval. It answers only within Rajesh/RABBIT/professional scope and redirects unrelated topics.

Example off-topic behavior:

```text
Question: how to go to Mumbai?
Behavior: polite professional redirect, no retrieval, no sources.
```

✅ **Visual answer markers added**

RABBIT can now use visual bullets in addition to normal bullets:

```text
✅ Green check
✔️ Check mark
☑️ Checked box
✓ Tick mark
🟢 Green status marker
📌 Context marker
🔎 Evidence marker
⚠️ Boundary/guardrail marker
```

The UI renderer supports these as visual bullets without removing existing plain bullet behavior.

## Verified Counts

Latest lifecycle API smoke test confirmed:

```text
canonical_ready_documents = 53
approved_chunks = 142
```

## Current Workflow Status

```text
Website extraction: done
Canonical RAG corpus: done
Chunking: done
Embeddings/Azure upload: done
RAG answer generation: working
User Mode: refined and tested
Lifecycle UI: first implementation complete, guarded log-only
Debug Mode: present but still needs optimization
Observability Mode: present but still needs optimization
Tech Mode: placeholder
Mobile/chat-widget polish: still pending
```

