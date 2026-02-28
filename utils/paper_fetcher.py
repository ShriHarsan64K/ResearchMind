"""
ResearchMind — Online Paper Fetcher
Fetches papers from arXiv, Semantic Scholar, CrossRef, CORE
IEEE, ResearchGate, Science Direct require login/API keys
so we show direct search links for those.
"""

import urllib.request
import urllib.parse
import json
import re
from datetime import datetime


def check_internet() -> bool:
    """Check if internet is available."""
    try:
        urllib.request.urlopen("https://arxiv.org", timeout=3)
        return True
    except:
        return False


# ── arXiv (100% free, no API key) ────────────────────────────────────────────
def fetch_arxiv(query: str, max_results: int = 8) -> list:
    """Fetch papers from arXiv — completely free and open."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={max_results}&sortBy=relevance"

        req = urllib.request.Request(url, headers={"User-Agent": "ResearchMind/2.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")

        papers = []
        entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)

        for entry in entries:
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            authors = re.findall(r'<name>(.*?)</name>', entry)
            link = re.search(r'<id>(.*?)</id>', entry)
            published = re.search(r'<published>(.*?)</published>', entry)

            if title and summary:
                papers.append({
                    "title": title.group(1).strip().replace("\n", " "),
                    "authors": ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
                    "abstract": summary.group(1).strip().replace("\n", " ")[:400] + "...",
                    "link": link.group(1).strip() if link else "",
                    "year": published.group(1)[:4] if published else "N/A",
                    "source": "arXiv",
                    "source_color": "#B31B1B",
                    "open_access": True
                })

        return papers
    except Exception as e:
        return [{"error": f"arXiv fetch failed: {str(e)}"}]


# ── Semantic Scholar (free, no key needed for basic) ─────────────────────────
def fetch_semantic_scholar(query: str, max_results: int = 8) -> list:
    """Fetch from Semantic Scholar — free academic search engine."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded}&limit={max_results}&fields=title,authors,abstract,year,externalIds,openAccessPdf"

        req = urllib.request.Request(url, headers={
            "User-Agent": "ResearchMind/2.0",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        papers = []
        for p in data.get("data", []):
            authors = [a.get("name", "") for a in p.get("authors", [])[:3]]
            pdf = p.get("openAccessPdf", {})
            papers.append({
                "title": p.get("title", "Unknown"),
                "authors": ", ".join(authors) + (" et al." if len(p.get("authors", [])) > 3 else ""),
                "abstract": (p.get("abstract", "No abstract available") or "No abstract available")[:400] + "...",
                "link": pdf.get("url", f"https://www.semanticscholar.org/search?q={encoded}"),
                "year": str(p.get("year", "N/A")),
                "source": "Semantic Scholar",
                "source_color": "#1857B6",
                "open_access": bool(pdf)
            })

        return papers
    except Exception as e:
        return [{"error": f"Semantic Scholar fetch failed: {str(e)}"}]


# ── CrossRef (free, 100M+ papers) ────────────────────────────────────────────
def fetch_crossref(query: str, max_results: int = 6) -> list:
    """Fetch from CrossRef — covers IEEE, Elsevier, Springer and more."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.crossref.org/works?query={encoded}&rows={max_results}&sort=relevance&select=title,author,abstract,published,URL,DOI,publisher"

        req = urllib.request.Request(url, headers={
            "User-Agent": "ResearchMind/2.0 (mailto:researchmind@nextstrike.dev)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        papers = []
        for p in data.get("message", {}).get("items", []):
            title_list = p.get("title", ["Unknown"])
            title = title_list[0] if title_list else "Unknown"

            authors = p.get("author", [])[:3]
            author_str = ", ".join([f"{a.get('given','')} {a.get('family','')}".strip() for a in authors])
            if len(p.get("author", [])) > 3:
                author_str += " et al."

            pub_date = p.get("published", {}).get("date-parts", [[None]])[0]
            year = str(pub_date[0]) if pub_date and pub_date[0] else "N/A"

            abstract = p.get("abstract", "Abstract not available")
            abstract = re.sub(r'<[^>]+>', '', abstract)[:400] + "..."

            papers.append({
                "title": title,
                "authors": author_str or "Unknown Authors",
                "abstract": abstract,
                "link": p.get("URL", f"https://doi.org/{p.get('DOI','')}"),
                "year": year,
                "source": f"CrossRef ({p.get('publisher','Publisher')[:20]})",
                "source_color": "#FF6B00",
                "open_access": False,
                "doi": p.get("DOI", "")
            })

        return papers
    except Exception as e:
        return [{"error": f"CrossRef fetch failed: {str(e)}"}]


# ── CORE (open access papers) ─────────────────────────────────────────────────
def fetch_core(query: str, max_results: int = 6) -> list:
    """Fetch from CORE — largest open access research aggregator."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.core.ac.uk/v3/search/works?q={encoded}&limit={max_results}"

        req = urllib.request.Request(url, headers={
            "User-Agent": "ResearchMind/2.0",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        papers = []
        for p in data.get("results", []):
            authors = p.get("authors", [])[:3]
            author_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in authors]

            papers.append({
                "title": p.get("title", "Unknown"),
                "authors": ", ".join(author_names) or "Unknown Authors",
                "abstract": (p.get("abstract", "No abstract") or "No abstract")[:400] + "...",
                "link": p.get("downloadUrl", "") or p.get("sourceFulltextUrls", [""])[0],
                "year": str(p.get("yearPublished", "N/A")),
                "source": "CORE (Open Access)",
                "source_color": "#00A86B",
                "open_access": True
            })

        return papers
    except Exception as e:
        return []


# ── Search Links for Paywalled Sources ───────────────────────────────────────
def get_search_links(query: str) -> list:
    """Generate direct search links for paywalled sources."""
    encoded = urllib.parse.quote(query)
    return [
        {
            "name": "IEEE Xplore",
            "url": f"https://ieeexplore.ieee.org/search/searchresult.jsp?queryText={encoded}",
            "color": "#00629B",
            "note": "Requires institutional access"
        },
        {
            "name": "ResearchGate",
            "url": f"https://www.researchgate.net/search?q={encoded}",
            "color": "#00D0AF",
            "note": "Free to browse abstracts"
        },
        {
            "name": "Science Direct",
            "url": f"https://www.sciencedirect.com/search?qs={encoded}",
            "color": "#FF6C00",
            "note": "Elsevier — requires access"
        },
        {
            "name": "Google Scholar",
            "url": f"https://scholar.google.com/scholar?q={encoded}",
            "color": "#4285F4",
            "note": "Free access"
        },
        {
            "name": "PubMed",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={encoded}",
            "color": "#336699",
            "note": "Free — biomedical focus"
        },
        {
            "name": "Springer",
            "url": f"https://link.springer.com/search?query={encoded}",
            "color": "#F36F21",
            "note": "Requires access for full text"
        },
    ]


# ── Main fetch function ───────────────────────────────────────────────────────
def fetch_all_sources(query: str) -> dict:
    """Fetch from all available free sources simultaneously."""
    results = {
        "arxiv": fetch_arxiv(query, 6),
        "semantic_scholar": fetch_semantic_scholar(query, 6),
        "crossref": fetch_crossref(query, 5),
        "core": fetch_core(query, 4),
        "search_links": get_search_links(query),
        "query": query,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # Count valid results
    total = sum(len([p for p in results[s] if "error" not in p])
                for s in ["arxiv", "semantic_scholar", "crossref", "core"])
    results["total_found"] = total

    return results


if __name__ == "__main__":
    print("Testing online paper fetcher...")
    print(f"Internet: {check_internet()}")
    results = fetch_all_sources("deep learning image classification")
    print(f"\narXiv: {len(results['arxiv'])} papers")
    print(f"Semantic Scholar: {len(results['semantic_scholar'])} papers")
    print(f"CrossRef: {len(results['crossref'])} papers")
    print(f"Total: {results['total_found']} papers found")
    if results['arxiv'] and 'error' not in results['arxiv'][0]:
        print(f"\nFirst arXiv paper: {results['arxiv'][0]['title']}")