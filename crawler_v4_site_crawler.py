# ============================================================
# CRAWLER V4 - CONTROLLED SITE CRAWLER
# Playwright-rendered, same-domain crawl, V3-style extraction
# ============================================================

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from ftfy import fix_text
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "01_input_seed_and_config"
RAW_HTML_DIR = BASE_DIR / "02_output_raw_html_rendered"
STRUCTURED_JSON_DIR = BASE_DIR / "03_output_structured_json"
CLEAN_JSON_DIR = BASE_DIR / "04_output_clean_json"
CLEAN_TEXT_DIR = BASE_DIR / "05_output_clean_text"
RAG_DOCUMENTS_DIR = BASE_DIR / "06_output_rag_documents"
REPORTS_DIR = BASE_DIR / "07_output_quality_reports_manifest"
LOGS_DIR = BASE_DIR / "08_output_logs"

for folder in [
    INPUT_DIR,
    RAW_HTML_DIR,
    STRUCTURED_JSON_DIR,
    CLEAN_JSON_DIR,
    CLEAN_TEXT_DIR,
    RAG_DOCUMENTS_DIR,
    REPORTS_DIR,
    LOGS_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)


DEFAULT_CONFIG = {
    "seed_url": "https://rajesharigala.com",
    "seed_urls": ["https://rajesharigala.com"],
    "max_pages": 40,
    "max_depth": 5,
    "delay_seconds": 1.0,
    "timeout_ms": 60000,
    "viewport_width": 1440,
    "viewport_height": 1800,
    "same_domain_only": True,
}

SKIP_EXTENSIONS = {
    ".7z",
    ".avi",
    ".bmp",
    ".css",
    ".csv",
    ".doc",
    ".docx",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".js",
    ".json",
    ".mov",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".rar",
    ".svg",
    ".tar",
    ".webm",
    ".webp",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}

SKIP_SCHEMES = {"mailto", "tel", "javascript", "data", "sms", "whatsapp"}
BAD_CHARACTER_PATTERNS = ["Â", "â", "ð", "Ã", "�"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = fix_text(text)

    replacements = {
        "\xa0": " ",
        "Systemsthat": "Systems that",
        "RÃ©sumÃ©": "Résumé",
        "â€¢": "•",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "Â": "",
        "ðŸŽ“": "",
        "ðŸ": "",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_duplicate_lines(lines: list[str]) -> list[str]:
    seen = set()
    result = []

    for line in lines:
        cleaned = clean_text(line)
        normalized = cleaned.lower()

        if cleaned and normalized not in seen:
            seen.add(normalized)
            result.append(cleaned)

    return result


def load_config(config_path: Path | None) -> dict:
    config = dict(DEFAULT_CONFIG)

    default_config_path = INPUT_DIR / "crawler_config.json"
    path_to_load = config_path or default_config_path

    if path_to_load.exists():
        user_config = json.loads(path_to_load.read_text(encoding="utf-8"))
        config.update(user_config)

    seed_file = INPUT_DIR / "seed_urls.txt"
    if seed_file.exists() and not config_path:
        seeds = [
            line.strip()
            for line in seed_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if seeds:
            config["seed_urls"] = seeds
            config["seed_url"] = seeds[0]

    if "seed_urls" not in config or not config["seed_urls"]:
        config["seed_urls"] = [config["seed_url"]]

    return config


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())

    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"

    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    if path.lower() in {"/index", "/index.html", "/home"}:
        path = "/"

    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    ignored_query_prefixes = ("utm_",)
    ignored_query_names = {"fbclid", "gclid", "msclkid"}
    filtered_pairs = [
        (key, value)
        for key, value in query_pairs
        if key not in ignored_query_names
        and not any(key.startswith(prefix) for prefix in ignored_query_prefixes)
    ]
    query = urlencode(filtered_pairs, doseq=True)

    return urlunparse((scheme, netloc, path, "", query, ""))


def is_same_domain(url: str, seed_domain: str) -> bool:
    return urlparse(url).netloc.lower().removeprefix("www.") == seed_domain


def should_skip_url(url: str, seed_domain: str, same_domain_only: bool) -> tuple[bool, str]:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme in SKIP_SCHEMES:
        return True, f"skipped_scheme:{scheme}"

    if scheme not in {"http", "https"}:
        return True, f"skipped_non_http_scheme:{scheme}"

    if same_domain_only and not is_same_domain(url, seed_domain):
        return True, "skipped_external_domain"

    lower_path = parsed.path.lower()
    if any(lower_path.endswith(ext) for ext in SKIP_EXTENSIONS):
        return True, "skipped_asset_extension"

    return False, ""


def sanitize_page_id(page_id: str) -> str:
    page_id = unquote(page_id.strip())
    page_id = re.sub(r"[^a-zA-Z0-9]+", "_", page_id).strip("_")
    page_id = re.sub(r"_+", "_", page_id)
    return page_id or "page"


def load_page_naming_map() -> dict[str, str]:
    naming_map_path = INPUT_DIR / "page_naming_map.json"

    if not naming_map_path.exists():
        return {}

    raw_map = json.loads(naming_map_path.read_text(encoding="utf-8"))
    return {normalize_url(url): sanitize_page_id(page_id) for url, page_id in raw_map.items()}


def page_id_from_url(url: str, naming_map: dict[str, str] | None = None) -> str:
    normalized_url = normalize_url(url)

    if naming_map and normalized_url in naming_map:
        return naming_map[normalized_url]

    parsed = urlparse(normalized_url)
    path = parsed.path.strip("/")

    if not path or path.lower() in {"index", "home"}:
        return "00_Homepage"

    decoded = unquote(path)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", decoded).strip("_").lower()
    slug = re.sub(r"_+", "_", slug)

    if not slug:
        slug = "page"

    if len(slug) > 90:
        digest = hashlib.sha1(normalized_url.encode("utf-8")).hexdigest()[:10]
        slug = f"{slug[:75]}_{digest}"

    return slug


def unique_page_id(url: str, used_ids: dict[str, str], naming_map: dict[str, str] | None = None) -> str:
    base_id = page_id_from_url(url, naming_map)

    if base_id not in used_ids:
        used_ids[base_id] = url
        return base_id

    if used_ids[base_id] == url:
        return base_id

    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    page_id = f"{base_id}_{digest}"
    used_ids[page_id] = url
    return page_id


def logical_parent_page_id(page_id: str, discovered_parent_page_id: str | None) -> str:
    if page_id == "00_Homepage":
        return "ROOT"

    if page_id in {"01_Business_Skills", "02_Technical_Skills", "03_AI_Projects", "04_GenAI"}:
        return "00_Homepage"

    if page_id.startswith("01_"):
        return "01_Business_Skills"

    if page_id.startswith("02_"):
        return "02_Technical_Skills"

    if page_id.startswith("03_"):
        return "03_AI_Projects"

    if page_id.startswith("04_"):
        return "04_GenAI"

    return discovered_parent_page_id or "00_Homepage"


def extract_links_from_soup(soup: BeautifulSoup, current_url: str) -> list[dict]:
    links = []
    seen_links = set()

    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text())
        href = urljoin(current_url, a["href"])
        normalized_href = normalize_url(href)

        if normalized_href not in seen_links:
            seen_links.add(normalized_href)
            links.append({"text": text, "href": normalized_href})

    return links


def extract_page_from_html(
    html: str,
    url: str,
    page_id: str,
    depth: int,
    parent_url: str | None,
    parent_page_id: str | None,
) -> dict:
    parsed = urlparse(url)
    soup = BeautifulSoup(html, "lxml")
    links = extract_links_from_soup(soup, url)

    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "form",
        "canvas",
        "iframe",
    ]):
        tag.decompose()

    title = clean_text(soup.title.get_text()) if soup.title else ""

    desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = clean_text(desc_tag.get("content", "")) if desc_tag else ""

    headings = []
    for level in ["h1", "h2", "h3", "h4"]:
        for h in soup.find_all(level):
            text = clean_text(h.get_text())
            if text:
                headings.append({"level": level, "text": text})

    paragraphs = []
    for p in soup.find_all("p"):
        text = clean_text(p.get_text())
        if text:
            paragraphs.append(text)

    main_content = soup.find("main")

    if main_content:
        main_text = main_content.get_text(" ", strip=True)
    else:
        main_text = soup.get_text(" ", strip=True)

    main_text = clean_text(main_text)

    return {
        "id": page_id,
        "source_type": "website_rendered_v4_site_crawl",
        "domain": parsed.netloc,
        "url": url,
        "depth": depth,
        "parent_url": parent_url,
        "parent_page_id": parent_page_id,
        "logical_parent_page_id": logical_parent_page_id(page_id, parent_page_id),
        "title": title,
        "meta_description": meta_description,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": links,
        "content": main_text,
        "crawl_timestamp": utc_now(),
    }


def build_rag_text(data: dict) -> str:
    lines = []

    lines.append(f"Title: {data['title']}")

    if data.get("meta_description"):
        lines.append(f"Meta Description: {data['meta_description']}")

    lines.append("")
    lines.append(f"Source URL: {data['url']}")

    lines.append("")
    lines.append("Headings:")
    for h in data["headings"]:
        lines.append(f"{h['level'].upper()}: {h['text']}")

    lines.append("")
    lines.append("Paragraphs:")
    for para in data["paragraphs"]:
        lines.append(para)

    lines.append("")
    lines.append("Main Content:")
    lines.append(data["content"])

    lines = remove_duplicate_lines(lines)
    rag_text = "\n".join(lines)
    return clean_text(rag_text)


def detect_suspicious_values(rag_text: str) -> list[dict]:
    patterns = [
        r"\b0\s+Years\s+Experience\b",
        r"\b0\s+Mentees\s+Guided\b",
        r"\b0\s+Industries\s+Served\b",
        r"\b0\s+Revenue\s+Impact\b",
        r"\b0\s+Projects\b",
        r"\b0\s+Clients\b",
        r"\b0\s+Accounts\b",
        r"\b0\s+KOLs\b",
        r"\b0\s+Plants\b",
    ]

    findings = []

    for pattern in patterns:
        for match in re.finditer(pattern, rag_text, flags=re.IGNORECASE):
            findings.append({
                "matched_text": match.group(0),
                "context": rag_text[max(0, match.start() - 100): match.end() + 100],
            })

    return findings


def bad_character_counts(text: str) -> dict[str, int]:
    return {pattern: text.count(pattern) for pattern in BAD_CHARACTER_PATTERNS}


def save_page_outputs(data: dict, html: str, rag_text: str, page_id: str) -> dict:
    raw_html_path = RAW_HTML_DIR / f"{page_id}.html"
    structured_json_path = STRUCTURED_JSON_DIR / f"{page_id}_structured.json"
    clean_json_path = CLEAN_JSON_DIR / f"{page_id}_clean.json"
    clean_text_path = CLEAN_TEXT_DIR / f"{page_id}_clean.txt"
    rag_file = RAG_DOCUMENTS_DIR / f"{page_id}_rag.txt"
    report_file = REPORTS_DIR / f"{page_id}_quality_report.json"

    data["raw_html_path"] = str(raw_html_path)

    raw_html_path.write_text(html, encoding="utf-8")
    structured_json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    clean_json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    clean_text_path.write_text(data["content"], encoding="utf-8")
    rag_file.write_text(rag_text, encoding="utf-8")

    suspicious = detect_suspicious_values(rag_text)
    report = {
        "version": "v4_site_crawler",
        "page_id": page_id,
        "url": data["url"],
        "depth": data["depth"],
        "parent_url": data["parent_url"],
        "parent_page_id": data["parent_page_id"],
        "logical_parent_page_id": data["logical_parent_page_id"],
        "title": data["title"],
        "characters_content": len(data["content"]),
        "words_content": len(data["content"].split()),
        "characters_rag_text": len(rag_text),
        "words_rag_text": len(rag_text.split()),
        "headings_count": len(data["headings"]),
        "paragraphs_count": len(data["paragraphs"]),
        "links_count": len(data["links"]),
        "bad_character_counts": bad_character_counts(rag_text),
        "suspicious_values": suspicious,
        "saved_files": {
            "raw_html": str(raw_html_path),
            "structured_json": str(structured_json_path),
            "clean_json": str(clean_json_path),
            "clean_text": str(clean_text_path),
            "rag_document": str(rag_file),
            "report": str(report_file),
        },
    }

    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return report


def render_page(page, url: str, timeout_ms: int) -> str:
    page.goto(url, wait_until="networkidle", timeout=timeout_ms)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2500)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)
    return page.content()


def crawl_site(config: dict) -> dict:
    seed_urls = [normalize_url(url) for url in config.get("seed_urls", [config["seed_url"]])]
    seed_url = seed_urls[0]
    seed_domain = urlparse(seed_url).netloc.lower().removeprefix("www.")
    max_pages = int(config["max_pages"])
    max_depth = int(config["max_depth"])
    delay_seconds = float(config["delay_seconds"])
    timeout_ms = int(config["timeout_ms"])
    same_domain_only = bool(config["same_domain_only"])
    naming_map = load_page_naming_map()

    queue = deque((url, 0, None) for url in seed_urls)
    queued = set(seed_urls)
    visited = set()
    used_ids = {}
    url_to_page_id = {}

    crawled_pages = []
    failed_pages = []
    skipped_urls = []
    discovered_internal_links = set()

    run_started_at = utc_now()

    print("============================================================")
    print("CRAWLER V4 SITE CRAWL STARTED")
    print("============================================================")
    print("Base directory:", BASE_DIR)
    print("Seed URL:", seed_url)
    print("Seed URLs:", len(seed_urls))
    for seed in seed_urls:
        print("-", seed)
    print("Seed domain:", seed_domain)
    print("Max pages:", max_pages)
    print("Max depth:", max_depth)
    print("Same domain only:", same_domain_only)
    print("Mapped page names:", len(naming_map))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={
                "width": int(config["viewport_width"]),
                "height": int(config["viewport_height"]),
            }
        )

        while queue and len(crawled_pages) < max_pages:
            current_url, depth, parent_url = queue.popleft()

            if current_url in visited:
                continue

            visited.add(current_url)

            if depth > max_depth:
                skipped_urls.append({
                    "url": current_url,
                    "reason": "skipped_max_depth",
                    "depth": depth,
                    "parent_url": parent_url,
                })
                continue

            skip, reason = should_skip_url(current_url, seed_domain, same_domain_only)
            if skip:
                skipped_urls.append({
                    "url": current_url,
                    "reason": reason,
                    "depth": depth,
                    "parent_url": parent_url,
                })
                continue

            page_id = unique_page_id(current_url, used_ids, naming_map)
            parent_page_id = url_to_page_id.get(parent_url) if parent_url else "ROOT"
            url_to_page_id[current_url] = page_id
            print(f"\n[{len(crawled_pages) + 1}/{max_pages}] depth={depth} id={page_id}")
            print("URL:", current_url)

            try:
                html = render_page(page, current_url, timeout_ms)
                data = extract_page_from_html(
                    html,
                    current_url,
                    page_id,
                    depth,
                    parent_url,
                    parent_page_id,
                )
                rag_text = build_rag_text(data)
                report = save_page_outputs(data, html, rag_text, page_id)
                crawled_pages.append(report)

                for link in data["links"]:
                    href = normalize_url(link["href"])
                    link_skip, link_reason = should_skip_url(href, seed_domain, same_domain_only)

                    if link_skip:
                        skipped_urls.append({
                            "url": href,
                            "reason": link_reason,
                            "depth": depth + 1,
                            "parent_url": current_url,
                        })
                        continue

                    discovered_internal_links.add(href)

                    if href not in visited and href not in queued and depth + 1 <= max_depth:
                        queue.append((href, depth + 1, current_url))
                        queued.add(href)

                print(
                    "Saved:",
                    f"words={report['words_content']}",
                    f"headings={report['headings_count']}",
                    f"links={report['links_count']}",
                )

            except PlaywrightTimeoutError as exc:
                failed_pages.append({
                    "url": current_url,
                    "depth": depth,
                    "parent_url": parent_url,
                    "parent_page_id": url_to_page_id.get(parent_url) if parent_url else "ROOT",
                    "error_type": "PlaywrightTimeoutError",
                    "error": str(exc),
                })
                print("FAILED timeout:", current_url)
            except Exception as exc:
                failed_pages.append({
                    "url": current_url,
                    "depth": depth,
                    "parent_url": parent_url,
                    "parent_page_id": url_to_page_id.get(parent_url) if parent_url else "ROOT",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                })
                print("FAILED:", current_url, type(exc).__name__, exc)

            if delay_seconds > 0 and queue and len(crawled_pages) < max_pages:
                time.sleep(delay_seconds)

        browser.close()

    hierarchy_table = [
        {
            "depth": page["depth"],
            "discovered_parent_page_id": page.get("parent_page_id"),
            "logical_parent_page_id": page.get("logical_parent_page_id"),
            "page_id": page["page_id"],
            "title": page["title"],
            "url": page["url"],
        }
        for page in sorted(crawled_pages, key=lambda item: (item["depth"], item["page_id"]))
    ]

    manifest = {
        "version": "v4_site_crawler",
        "run_started_at": run_started_at,
        "run_finished_at": utc_now(),
        "config": {
            "seed_url": seed_url,
            "seed_urls": seed_urls,
            "seed_domain": seed_domain,
            "max_pages": max_pages,
            "max_depth": max_depth,
            "delay_seconds": delay_seconds,
            "timeout_ms": timeout_ms,
            "same_domain_only": same_domain_only,
        },
        "counts": {
            "pages_crawled": len(crawled_pages),
            "pages_failed": len(failed_pages),
            "urls_skipped": len(skipped_urls),
            "internal_links_discovered": len(discovered_internal_links),
            "urls_remaining_in_queue": len(queue),
        },
        "hierarchy_table": hierarchy_table,
        "crawled_pages": crawled_pages,
        "failed_pages": failed_pages,
        "skipped_urls": skipped_urls,
        "discovered_internal_links": sorted(discovered_internal_links),
    }

    manifest_path = REPORTS_DIR / "crawl_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n============================================================")
    print("CRAWLER V4 SITE CRAWL COMPLETED")
    print("============================================================")
    print("Pages crawled:", len(crawled_pages))
    print("Pages failed:", len(failed_pages))
    print("URLs skipped:", len(skipped_urls))
    print("Internal links discovered:", len(discovered_internal_links))
    print("Manifest:", manifest_path)

    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Controlled same-domain Playwright site crawler with V3-style extraction."
    )
    parser.add_argument("--seed-url", help="Seed URL to start crawling.")
    parser.add_argument("--max-pages", type=int, help="Maximum pages to crawl.")
    parser.add_argument("--max-depth", type=int, help="Maximum crawl depth.")
    parser.add_argument("--delay-seconds", type=float, help="Delay between pages.")
    parser.add_argument("--config", type=Path, help="Optional JSON config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    if args.seed_url:
        config["seed_url"] = args.seed_url
        config["seed_urls"] = [args.seed_url]
    if args.max_pages is not None:
        config["max_pages"] = args.max_pages
    if args.max_depth is not None:
        config["max_depth"] = args.max_depth
    if args.delay_seconds is not None:
        config["delay_seconds"] = args.delay_seconds

    print("Python executable:", sys.executable)
    crawl_site(config)


if __name__ == "__main__":
    main()
