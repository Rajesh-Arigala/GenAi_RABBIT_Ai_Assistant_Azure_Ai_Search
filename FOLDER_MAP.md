# V4 Site Crawler Folder Map

This folder is isolated for `crawler_v4_site_crawler.py`.

The folder names intentionally show the input/output flow. If this naming feels too heavy after testing, we can revert to the simpler existing style.

## Full Flow

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
07_output_quality_reports_manifest/
  ↓
09_future_output_chunks/   later phase
```

Runtime logs go to:

```text
08_output_logs/
```

Planning and notes go to:

```text
10_working_docs/
```

## Root Folder

```text
v4_site_crawler/
```

Purpose:

- Main isolated execution area for the V4 complete-website crawler.
- Future location for `crawler_v4_site_crawler.py`.
- Keeps V4 separate from all older V0/V3 execution folders.

Expected root files:

- `crawler_v4_site_crawler.py`
- `FOLDER_MAP.md`

## `01_input_seed_and_config/`

Input:

- Optional seed/config files for the crawler.

Possible files:

```text
01_input_seed_and_config/
  seed_urls.txt
  crawler_config.json
```

Purpose:

- Store manual crawler inputs if we do not want to hardcode them.
- Examples: seed URL, max depth, max pages, include paths, exclude paths.

Current expected first seed:

```text
https://rajesharigala.com
```

## `02_output_raw_html_rendered/`

Input:

- Rendered page content from Playwright.

Output:

- One rendered HTML file per crawled webpage.

Example:

```text
02_output_raw_html_rendered/
  homepage.html
  mlops_ml_ops.html
  mlops_ai6_ai6_3.html
```

Purpose:

- Preserve the exact Playwright-rendered HTML used for extraction.
- Use this only for debugging extraction issues.

Do not send this to Azure AI Search.

## `03_output_structured_json/`

Input:

- Rendered HTML from `02_output_raw_html_rendered/`.

Output:

- One full structured JSON document per webpage.

Example:

```text
03_output_structured_json/
  homepage_structured.json
  mlops_ml_ops_structured.json
```

Expected contents:

- Page ID.
- URL.
- Domain.
- Title.
- Meta description.
- Headings.
- Paragraphs.
- Links.
- Main content.
- Crawl timestamp.
- Raw HTML path.
- Quality metadata.

Purpose:

- Main machine-readable extraction artifact.
- Best source for future chunking because it preserves page metadata.

## `04_output_clean_json/`

Input:

- Structured JSON from `03_output_structured_json/`.

Output:

- One simplified clean JSON file per webpage.

Example:

```text
04_output_clean_json/
  homepage_clean.json
  mlops_ml_ops_clean.json
```

Purpose:

- Cleaner JSON for downstream processing.
- May initially match structured JSON.
- Can later become a reduced format optimized for chunking.

## `05_output_clean_text/`

Input:

- Cleaned main content from each page.

Output:

- One plain clean text file per webpage.

Example:

```text
05_output_clean_text/
  homepage_clean.txt
  mlops_ml_ops_clean.txt
```

Purpose:

- Human-readable page text.
- Manual QA checkpoint.
- Useful for checking if extraction is clean before chunking.

## `06_output_rag_documents/`

Input:

- Title, meta description, headings, paragraphs, and clean main content.

Output:

- One RAG-ready text document per webpage.

Example:

```text
06_output_rag_documents/
  homepage_rag.txt
  mlops_ml_ops_rag.txt
```

Purpose:

- Main text source for future chunking.
- Recommended input for `chunking_v1.py`.

## `07_output_quality_reports_manifest/`

Input:

- Extraction stats, QA checks, crawl decisions, and output paths.

Output:

- One page-level quality report per webpage.
- One site-level crawl manifest.

Example:

```text
07_output_quality_reports_manifest/
  homepage_quality_report.json
  mlops_ml_ops_quality_report.json
  crawl_manifest.json
```

Page-level report should include:

- URL.
- Page ID.
- Title.
- Word count.
- Character count.
- Heading count.
- Paragraph count.
- Link count.
- Bad character counts.
- Suspicious zero KPI values.
- Output file paths.

Site-level manifest should include:

- Seed URL.
- Max depth.
- Max pages.
- Pages crawled.
- Pages skipped.
- Pages failed.
- Internal links discovered.
- Output files for each page.

Purpose:

- Main audit trail.
- Review checkpoint before chunking.

## `08_output_logs/`

Input:

- Runtime crawler messages.

Output:

- Optional run logs.

Example:

```text
08_output_logs/
  crawl_2026_06_17.log
```

Purpose:

- Debug failed pages.
- Record crawl progress.
- Keep runtime logs separate from extraction artifacts.

## `09_future_output_chunks/`

Input:

- RAG documents from `06_output_rag_documents/`.
- Or clean JSON from `04_output_clean_json/`.

Output:

- Future chunk files for Azure AI Search.

Example:

```text
09_future_output_chunks/
  chunks_v1.jsonl
  chunks_v1_manifest.json
```

Purpose:

- Reserved for the next phase after website extraction is approved.
- Not used by the V4 crawler itself.

Future chunk record example:

```json
{
  "chunk_id": "homepage_001",
  "source_page_id": "homepage",
  "source_url": "https://rajesharigala.com",
  "title": "Rajesh Arigala | AI & GenAI Systems",
  "content": "..."
}
```

## `10_working_docs/`

Input:

- Planning notes.
- Design decisions.
- Review documents.

Output:

- V4-specific documentation.

Example:

```text
10_working_docs/
  v4_guardrails.md
  v4_run_notes.md
  v4_review_findings.md
```

Purpose:

- Keep V4 decisions separate from older crawler documentation.
- Store guardrails, run summaries, and future handover notes.

## What Goes To Azure AI Search Later

Do not send raw HTML to Azure AI Search.

Recommended future Azure AI Search input:

```text
09_future_output_chunks/chunks_v1.jsonl
```

Each chunk should include:

- Chunk text.
- Page title.
- Source URL.
- Page ID.
- Section heading if available.
- Crawl timestamp.

## What Goes To S3 Later

Recommended S3 backup/source-of-truth:

```text
02_output_raw_html_rendered/
03_output_structured_json/
04_output_clean_json/
05_output_clean_text/
06_output_rag_documents/
07_output_quality_reports_manifest/
```

S3 can preserve full artifacts. Azure AI Search should receive only clean searchable chunks.

