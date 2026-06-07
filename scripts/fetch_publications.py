#!/usr/bin/env python3
"""
Fetch publications for Bramsh Qamar Chandio from Semantic Scholar API.
Writes data/publications.json, which Hugo renders at build time.

Usage:
    python3 scripts/fetch_publications.py
"""

import json
import os
import time
import urllib.request
import urllib.error
from datetime import date

AUTHOR_ID = "1752544717"
API_BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,authors,year,venue,externalIds,publicationDate,openAccessPdf"

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT_PATH = os.path.join(ROOT, "data", "publications.json")

# Corrections for papers where Semantic Scholar records the preprint year
# instead of the journal/conference publication year.
# Key: S2 paperId. Any field listed here overrides the API value.
OVERRIDES = {
    # BundleWarp: S2 has 2023 bioRxiv preprint; published Medical Image Analysis 2026.
    "b71a8f5e4554a313b3656a11702a866641ab01d0": {
        "title": "BundleWarp: Enhancing white matter tractometry and morphometry with precise neuronal mapping using streamline-based nonlinear registration",
        "year": 2026,
        "venue": "Medical Image Analysis",
        "doi": "10.1016/j.media.2026.104114",
        "publicationDate": "2026-01-01",
    },
    # Assessing the Influence: S2 year=2025 (bioRxiv); ISBI 2026. Also fixes missing apostrophe.
    "f3ae72744640e957d35eee6916da997b325cc532": {
        "title": "Assessing the Influence of Tractography Methods on White Matter Microstructure and Tractometry Analysis in Alzheimer's Disease",
        "year": 2026,
        "venue": "2026 IEEE 23rd International Symposium on Biomedical Imaging (ISBI)",
    },
    # Evaluating Sample-Size Efficiency: S2 year=2025 (bioRxiv); ISBI 2026.
    "6aed84a9fb1e6a50d0012746bcac9c2ee9c5ab1e": {
        "year": 2026,
        "venue": "2026 IEEE 23rd International Symposium on Biomedical Imaging (ISBI)",
    },
}

# Papers missing from Semantic Scholar entirely. Each entry must include at minimum:
# title, authors (list of {name, authorId}), year, venue, url.
ADDITIONS = []


def get(url, retries=6):
    req = urllib.request.Request(url, headers={"User-Agent": "BMNLab-website/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = 2 ** attempt * 5
                print(f"  HTTP {e.code}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
        except urllib.error.URLError as e:
            wait = 2 ** attempt * 3
            print(f"  Network error ({e.reason}). Waiting {wait}s...")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {retries} retries: {url}")


def fetch_papers():
    papers = []
    offset = 0
    limit = 100
    while True:
        url = (
            f"{API_BASE}/author/{AUTHOR_ID}/papers"
            f"?fields={FIELDS}&limit={limit}&offset={offset}"
        )
        data = get(url)
        batch = data.get("data", [])
        papers.extend(batch)
        print(f"  {len(papers)} papers fetched...")
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(1)
    return papers


def format_paper(p):
    authors = [
        {"name": a.get("name", ""), "authorId": a.get("authorId") or ""}
        for a in p.get("authors", [])
    ]
    ext = p.get("externalIds") or {}
    doi = ext.get("DOI", "")
    paper_id = p.get("paperId", "")
    url = f"https://doi.org/{doi}" if doi else (
        f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else ""
    )
    pdf = (p.get("openAccessPdf") or {}).get("url", "")
    return {
        "title": normalize_title(p.get("title") or ""),
        "authors": authors,
        "year": p.get("year"),
        "venue": p.get("venue") or "",
        "doi": doi,
        "url": url,
        "pdf": pdf,
        "publicationDate": p.get("publicationDate") or "",
        "paperId": paper_id,
    }


# Acronyms that should stay uppercase when normalizing all-caps titles.
_ACRONYMS = {
    'mri', 'fmri', 'dti', 'dki', 'dwi', 'fa', 'md', 'rd',
    'buan', 'ieee', 'isbi', 'ismrm', 'sipaim', 'embc', 'miccai', 'dipy',
    'adni', 'habs', 'ppmi', 'hcp', 'apoe', 'mci', 'asd', 'bd', 'ms',
    'ct', 'pet', 'ai', 'ml', 'snr', 'gm', 'wm', 'csf',
}
_LOWERCASE_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'nor', 'for', 'so',
    'at', 'by', 'in', 'of', 'on', 'to', 'up', 'as', 'with',
    'from', 'into', 'over', 'after', 'via', 'vs',
}


def _cap_word(w):
    """Capitalize one word, preserving known acronyms and handling hyphens."""
    if '-' in w:
        return '-'.join(_cap_word(p) for p in w.split('-'))
    core = w.rstrip('.,;:)')
    suffix = w[len(core):]
    return (core.upper() if core in _ACRONYMS else core.capitalize()) + suffix


def normalize_title(title):
    """Convert suspiciously all-caps titles to title case."""
    letters = [c for c in title if c.isalpha()]
    if not letters or sum(c.isupper() for c in letters) / len(letters) <= 0.8:
        return title
    words = title.lower().split()
    return ' '.join(
        _cap_word(w) if i == 0 or w.rstrip('.,;:)') not in _LOWERCASE_WORDS
        else w
        for i, w in enumerate(words)
    )


PREPRINT_VENUES = {"biorxiv", "arxiv", "medrxiv", "ssrn", "psyarxiv", "chemrxiv"}


def is_preprint(venue):
    return venue.strip().lower() in PREPRINT_VENUES


def apply_overrides(papers):
    result = []
    for p in papers:
        patch = OVERRIDES.get(p["paperId"])
        if patch:
            p = {**p, **patch}
            if "doi" in patch and patch["doi"]:
                p["url"] = f"https://doi.org/{patch['doi']}"
        result.append(p)
    existing_ids = {p["paperId"] for p in result}
    for addition in ADDITIONS:
        if addition.get("paperId") not in existing_ids:
            result.append(addition)
    return result


def deduplicate(papers):
    """One entry per title: prefer published over preprint, then higher year."""
    by_title = {}
    for p in papers:
        key = p["title"].lower().strip()
        if key not in by_title:
            by_title[key] = p
            continue
        existing = by_title[key]
        e_pre, p_pre = is_preprint(existing["venue"]), is_preprint(p["venue"])
        if e_pre and not p_pre:
            by_title[key] = p
        elif not e_pre and p_pre:
            pass
        else:
            e_year, p_year = existing["year"] or 0, p["year"] or 0
            if p_year > e_year or (
                p_year == e_year
                and (p["publicationDate"] or "") > (existing["publicationDate"] or "")
            ):
                by_title[key] = p
    return list(by_title.values())


def main():
    print("Fetching papers from Semantic Scholar API...")
    raw = fetch_papers()
    print(f"Total from API: {len(raw)}")

    papers = [format_paper(p) for p in raw]
    papers = apply_overrides(papers)

    before = len(papers)
    papers = deduplicate(papers)
    if before - len(papers):
        print(f"Removed {before - len(papers)} duplicate(s)")

    papers.sort(key=lambda p: (p["year"] or 0, p["publicationDate"] or ""), reverse=True)

    os.makedirs(os.path.dirname(os.path.abspath(OUT_PATH)), exist_ok=True)
    output = {
        "lastUpdated": date.today().isoformat(),
        "authorId": AUTHOR_ID,
        "papers": papers,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(papers)} papers -> {OUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        print("Keeping existing data/publications.json as fallback.")
        raise SystemExit(1)
