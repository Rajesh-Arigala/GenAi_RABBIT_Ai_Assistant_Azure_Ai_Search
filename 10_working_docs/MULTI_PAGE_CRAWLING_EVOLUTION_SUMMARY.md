# Multi-Page Crawling Evolution Summary

## Purpose

This document summarizes the evolution from a single-page crawler into the isolated V4 multi-page website crawler and RAG corpus pipeline.

Original root:

```text
/Users/jhonny001/Desktop/website-data-store
```

Standalone RABBIT project root:

```text
/Users/jhonny001/Desktop/RABBIT_Assistant
```

## Why V4 Was Created

After the homepage extraction reached an approved V3 baseline, the next problem was not extraction quality for one page. The next problem was controlled extraction for a full website hierarchy.

Need:

- Crawl multiple pages.
- Preserve hierarchy.
- Name files consistently.
- Avoid mixing V4 outputs with older V0/V3 runs.
- Produce RAG-ready documents for chunking and Azure AI Search.
- Keep a handoff trail so future sessions can understand the corpus.

## V4 Isolation Decision

A separate folder was created for V4 execution:

```text
v4_site_crawler/
```

Reason:

- Keep complete-site crawling separate from earlier one-page experiments.
- Preserve older crawler outputs.
- Make input/output flow clear.
- Allow rollback if V4 naming or structure became too heavy.

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
  ↓
09_future_output_chunks/
  ↓
13_output_azure_ready/
  ↓
14_output_embeddings/
```

Supporting folders:

```text
08_output_logs/
10_working_docs/
16_retrieval_testing/
17_answer_generation/
18_flask_chat_ui/
```

## Naming Evolution

The file naming convention evolved from URL slugs to hierarchy-aware names.

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

Reason:

- File names should show hierarchy.
- Page IDs should remain stable for chunking and Azure metadata.
- Parent-child relationships should be understandable from file names.
- Dashboard hierarchy should match the document corpus.

## Hierarchy Decisions

Top-level view:

```text
00_Homepage
01_Business_Skills
02_Tech_01_Technical_Skills
02_Tech_02_MLOps
03_AI_Projects
04_GenAI
```

Important clarification:

- `03_AI_Projects` is a visual parent section with approved child pages.
- `04_GenAI` is a future placeholder.
- `02_Tech_02_MLOps` is a visual parent for MLOps subsections.
- Parent placeholders may exist even when they do not have separate chunkable RAG documents.

## Crawl Depth Understanding

The website depth was understood as approximately:

```text
Homepage
  ↓
Skill section page
  ↓
Skill/project group page
  ↓
Project page
  ↓
Project detail pages
```

Example:

```text
Homepage
  ↓
MLOps page
  ↓
CI/CD page
  ↓
CI/CD child project pages
```

The crawler approach was controlled rather than fully uncontrolled deep crawling, because naming, hierarchy, and RAG readiness mattered more than raw link volume.

## Section Completion

Approved final corpus summary:

| Section | Expected Pages | Ready Pages |
|---|---:|---:|
| 00_Homepage | 1 | 1 |
| 01_Business_Skills | 7 | 7 |
| 02_Tech_01_Technical_Skills | 8 | 8 |
| 02_Tech_02_MLOps_01_CICD | 6 | 6 |
| 02_Tech_02_MLOps_02_Containers | 9 | 9 |
| 02_Tech_02_MLOps_03_MLOps_ML_Systems | 2 | 2 |
| 02_Tech_02_MLOps_04_IaC | 3 | 3 |
| 03_AI_Projects | 17 | 17 |

Totals:

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

## Canonical Corpus Decision

Canonical folder for chunking:

```text
06_output_rag_documents_ready/
```

Canonical document count:

```text
53
```

Noncanonical/staging folder:

```text
06_output_rag_documents/
```

Observed broader file count:

```text
73
```

Decision:

- Use the 53 approved ready documents for chunking and Azure AI Search.
- Treat the broader 73-file folder as staging/legacy/noncanonical until cleaned.
- Do not use every file in `06_output_rag_documents/` blindly.

## Cross-Reference Evolution

Some pages naturally point to common related pages. Instead of duplicating content, a cross-reference report was created.

File:

```text
07_output_quality_reports_manifest/V4_Cross_Reference_Report.md
```

Purpose:

- Preserve relationships between MLOps sections and related AI project pages.
- Use cross-reference metadata during chunking and retrieval.
- Avoid duplicating the same page content under multiple parents.

Recommendation:

```text
Use cross-reference data as metadata, not as duplicate content.
```

## Quality/Readiness Reports

Section readiness reports were created for:

```text
00_Homepage
01_Business_Skills
02_Tech_01_Technical_Skills
02_Tech_02_MLOps_01_CICD
02_Tech_02_MLOps_02_Containers
02_Tech_02_MLOps_03_MLOps_ML_Systems
02_Tech_02_MLOps_04_IaC
03_AI_Projects
```

Master manifest:

```text
07_output_quality_reports_manifest/V4_Final_Corpus_Manifest.md
```

Status:

```text
READY_FOR_CHUNKING_PREP
```

## GenAI Status

`04_GenAI` exists as a future placeholder.

Current rule:

- Do not claim dedicated GenAI project pages are ready until they are actually crawled and added.
- RABBIT can discuss GenAI direction and capability, but should not invent a completed GenAI project corpus.

## Handoff For Multi-Page Pipeline

Approved way forward:

1. Use the V4 hierarchy and page IDs as source of truth.
2. Use `06_output_rag_documents_ready/` as canonical chunking input.
3. Use cross-reference report as metadata.
4. Keep placeholders visible for future dashboard/document lifecycle.
5. Chunk only approved ready documents.
6. Embed approved chunks.
7. Upload to Azure AI Search.
8. Use Debug/Observability modes to validate retrieval and answer quality.

## Why This Matters For RABBIT

RABBIT is not only a chat UI. It depends on a traceable ingestion chain:

```text
Website pages
  ↓
V4 crawler
  ↓
RAG-ready documents
  ↓
chunks
  ↓
embeddings
  ↓
Azure AI Search
  ↓
RABBIT answer generation
```

If the crawler hierarchy is clean, later retrieval, debug mode, source links, and document lifecycle management become much easier.
