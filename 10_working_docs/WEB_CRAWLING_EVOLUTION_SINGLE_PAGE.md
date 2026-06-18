# Web Crawling Evolution - Single Page

## Purpose

This document summarizes the evolution of the single-page extraction work done in:

```text
/Users/jhonny001/Desktop/website-data-store
```

The original goal was to extract Rajesh Arigala's homepage cleanly enough for downstream RAG use. The work evolved through static crawling, Playwright rendering, noisy high-recall extraction, and finally a clean V3 baseline.

## Original Problem

The homepage had rendered/dynamic content that was not reliably captured by a simple static HTML crawler. KPI/counter values were especially important because wrong values would create wrong RAG answers.

Examples of the issue:

```text
0 Years Experience
0 Mentees Guided
0 Industries Served
```

This pointed to JavaScript-rendered counters and dynamic content.

## Version Timeline

## V0 - Static Crawler

File:

```text
crawler_v0.py
```

Technology:

```text
requests
BeautifulSoup
ftfy
```

Role:

- Static fallback crawler.
- Fast and simple.
- Good for non-JavaScript pages.

Observed metrics:

```text
content words: 1,177
content chars: 8,817
headings: 42
paragraphs: 33
links: 23
```

Strengths:

- Stable and easy to run.
- No browser dependency.
- Clean enough for simple/static pages.

Limitations:

- Does not execute JavaScript.
- Misses rendered/lazy content.
- Misses content compared with the final V3 extraction.

Practical accuracy:

```text
Static extraction: about 85-90%
Rendered webpage extraction: about 75-85%
Overall homepage usefulness: about 80-85%
```

Status:

```text
Keep as fallback only.
```

## V1 - Cleaning Iterations

Role:

- Intermediate cleanup experiments.
- UTF-8 cleanup.
- Noise removal.
- Early RAG document shaping.

Status:

```text
Archived and superseded.
```

## Playwright Experiment

Issue discovered:

- Static extraction was not enough.
- KPI counters needed rendered browser execution.

Decision:

```text
Introduce Playwright.
```

Important runtime lesson:

- Playwright sync API should be run as a standalone Python script from terminal.
- Running inside notebook caused async loop issues.

## First Playwright Crawler

File:

```text
crawler_playwright.py
```

Technology:

```text
Playwright
BeautifulSoup
ftfy
```

Observed metrics:

```text
content words: 1,355
RAG words: 1,633
headings: 52
paragraphs: 43
links: 23
```

Strengths:

- Rendered the webpage.
- Captured much more content than V0.
- Got all headings/paragraphs seen in V3.

Problem:

- Had hardcoded KPI patching logic.
- Hardcoded values can silently become stale.

Example stale KPI risk:

```text
15+ Years Experience
100+ Mentees Guided
```

Later approved values:

```text
13+ Years Experience
15+ Mentees Guided
```

Status:

```text
Historical reference only.
```

## V2 - High Recall Playwright Debug Crawler

File:

```text
crawler_playwright_v2.py
```

Role:

- Debugging crawler for rendered content and KPI/counter discovery.

Observed metrics:

```text
content words: 1,371
RAG words: 10,383
RAG chars: 79,454
headings: 52
paragraphs: 43
links: 23
counter candidates: 83
suspicious counters: 0
```

Strengths:

- Excellent recall.
- Captured rendered content.
- Useful for investigating counters/dynamic DOM blocks.

Problem:

- RAG output was far too large.
- Pulled parent/container/body blocks.
- Created massive duplication and noise.

Practical accuracy:

```text
Completeness/recall: 95-100%
Clean extraction precision: 50-60%
RAG usefulness: 60-70%
```

Status:

```text
Keep only as debugging/reference crawler.
```

## V3 - Approved Single-Page Baseline

File:

```text
crawler_v3.py
```

Technology:

```text
Playwright
BeautifulSoup
ftfy
```

Role:

- Clean rendered extraction baseline.
- Approved source for single-page extraction.

Observed metrics:

```text
content words: 1,371
content chars: 10,130
RAG words: 2,210
RAG chars: 16,442
headings: 52
paragraphs: 43
links: 23
suspicious zero KPI values: 0
```

Validated KPI values:

```text
13+ Years Experience
₹50L+ Revenue Impact
15+ Mentees Guided
6+ Industries Served
₹4.73 Cr
₹625 Cr
835+
100 Accounts
15 KOLs
```

Strengths:

- Executes JavaScript.
- Scrolls/lazily loads content.
- Removes non-content elements.
- Extracts title, meta description, headings, paragraphs, links, main content.
- Builds clean RAG text.
- Avoids hardcoded KPI patching.
- Writes a quality report.

Practical accuracy:

```text
Content capture: 95-100%
Clean text extraction: 90-95%
RAG readiness: 90-95%
Overall current homepage accuracy: 90-95%
```

Status:

```text
Approved single-page extraction baseline.
```

## Why V3 Won

V2 and V3 captured the same content volume:

```text
V2 content words: 1,371
V3 content words: 1,371
```

But their RAG output differed sharply:

```text
V2 RAG words: 10,383
V3 RAG words: 2,210
```

Conclusion:

- V2 was not extracting more useful content.
- It was extracting duplicate/noisy DOM text.
- V3 preserved meaningful content while removing noise.

## Single-Page Handoff

Approved way forward for single-page extraction:

1. Use V3-style Playwright rendering.
2. Avoid hardcoded page-specific patches.
3. Preserve structured JSON, clean text, RAG text, and quality reports.
4. Use V2 only when debugging missing dynamic values.
5. Use V0 only as static fallback.
6. Freeze V3 as the known-good single-page baseline.

## Output Artifacts

Original single-page folders:

```text
raw_html/
structured_json/
clean_json/
clean_text/
rag_documents/
reports/
logs/
working_docs/
```

These were the foundation for the later V4 multi-page crawler.
