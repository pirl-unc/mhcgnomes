#!/usr/bin/env python3
"""
Collect MHC allele strings from all candidate papers.

For each paper in candidate_papers.tsv:
1. Look up PMC ID (if available) via Entrez
2. Download supplementary files from PMC OA or publisher
3. Scrape for MHC allele strings
4. Output consolidated validation TSV

Usage:
    python paper/scripts/collect_all.py
"""

import csv
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

try:
    from Bio import Entrez
except ImportError:
    print("Requires biopython: pip install biopython", file=sys.stderr)
    sys.exit(1)

Entrez.email = "mhcgnomes-paper@example.com"

ROOT = Path(__file__).resolve().parent.parent.parent
CANDIDATES = ROOT / "paper" / "validation" / "candidate_papers.tsv"
RAW_DIR = ROOT / "paper" / "raw"
VAL_DIR = ROOT / "paper" / "validation"
SCRAPE_SCRIPT = ROOT / "paper" / "scripts" / "scrape_paper.py"


def pmid_to_pmc(pmid):
    """Convert PMID to PMCID via Entrez."""
    try:
        handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
        result = Entrez.read(handle)
        handle.close()
        for linkset in result:
            for db_link in linkset.get("LinkSetDb", []):
                if db_link.get("DbTo") == "pmc":
                    links = db_link.get("Link", [])
                    if links:
                        return links[0]["Id"]
    except Exception:
        pass
    return None


def get_pmc_supp_urls(pmc_id):
    """Get supplementary file URLs from PMC OA service."""
    urls = []
    try:
        oa_url = (
            f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?"
            f"id=PMC{pmc_id}"
        )
        req = urllib.request.Request(oa_url, headers={"User-Agent": "mhcgnomes-paper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode()
            # Parse XML for links
            for m in re.finditer(r'href="(https?://[^"]+)"', text):
                href = m.group(1)
                if any(ext in href.lower() for ext in [".xlsx", ".xls", ".csv", ".tsv", ".zip", ".tar"]):
                    urls.append(href)
    except Exception:
        pass

    # Also try the PMC supplementary page directly
    try:
        supp_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/bin/"
        req = urllib.request.Request(supp_url, headers={"User-Agent": "mhcgnomes-paper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode()
            for m in re.finditer(r'href="([^"]*\.(xlsx|xls|csv|tsv|txt|zip|docx))"', text, re.IGNORECASE):
                href = m.group(1)
                if not href.startswith("http"):
                    href = f"https://www.ncbi.nlm.nih.gov{href}" if href.startswith("/") else f"{supp_url}{href}"
                urls.append(href)
    except Exception:
        pass

    return list(set(urls))


def get_doi_supp_urls(doi):
    """Try to find supplementary files via DOI redirect."""
    if not doi:
        return []
    urls = []
    try:
        # Follow DOI redirect to get publisher page
        req = urllib.request.Request(
            f"https://doi.org/{doi}",
            headers={"User-Agent": "mhcgnomes-paper/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            final_url = resp.url
            text = resp.read().decode(errors="replace")

        # Look for supplementary file links
        for m in re.finditer(
            r'href="([^"]*(?:supplementa|supp|S\d+|table_S|Table_S|additional)[^"]*'
            r'\.(?:xlsx|xls|csv|tsv|zip|txt))"',
            text,
            re.IGNORECASE,
        ):
            href = m.group(1)
            if not href.startswith("http"):
                from urllib.parse import urljoin
                href = urljoin(final_url, href)
            urls.append(href)
    except Exception:
        pass
    return list(set(urls))


def download_file(url, dest):
    """Download a URL to a local path."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mhcgnomes-paper/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(dest, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"    Download failed: {e}", file=sys.stderr)
        return False


def scrape_file(filepath, species, source, output):
    """Run scrape_paper.py on a file."""
    try:
        result = subprocess.run(
            [
                sys.executable, str(SCRAPE_SCRIPT),
                "--input", str(filepath),
                "--species", species,
                "--source", source,
                "--output", str(output),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            # Count lines
            lines = sum(1 for _ in open(output)) - 1  # subtract header
            return lines
        else:
            print(f"    Scrape error: {result.stderr[:200]}", file=sys.stderr)
    except Exception as e:
        print(f"    Scrape error: {e}", file=sys.stderr)
    return 0


def load_candidates():
    """Load candidate papers from TSV."""
    papers = []
    with open(CANDIDATES) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            papers.append(row)
    return papers


def main():
    papers = load_candidates()
    print(f"Processing {len(papers)} candidate papers...\n", file=sys.stderr)

    total_strings = 0
    papers_with_data = 0
    papers_no_supp = 0
    papers_no_mhc = 0

    all_validation_rows = []

    for i, paper in enumerate(papers):
        pmid = paper["pmid"]
        stratum = paper["stratum"]
        title = paper["title"][:70]
        doi = paper.get("doi", "")

        print(f"[{i+1}/{len(papers)}] PMID:{pmid} ({stratum}) {title}...", file=sys.stderr)

        # Create output directory
        safe_id = f"PMID_{pmid}"
        raw_dir = RAW_DIR / safe_id
        raw_dir.mkdir(parents=True, exist_ok=True)

        # Find supplementary files
        pmc_id = pmid_to_pmc(pmid)
        supp_urls = []
        if pmc_id:
            print(f"  PMC{pmc_id}", file=sys.stderr)
            supp_urls = get_pmc_supp_urls(pmc_id)

        if not supp_urls and doi:
            supp_urls = get_doi_supp_urls(doi)

        if not supp_urls:
            print(f"  No supplementary files found", file=sys.stderr)
            papers_no_supp += 1
            time.sleep(0.3)
            continue

        print(f"  Found {len(supp_urls)} supplementary URLs", file=sys.stderr)

        # Download and scrape each file
        paper_strings = 0
        for url in supp_urls[:5]:  # limit to 5 files per paper
            filename = url.split("/")[-1].split("?")[0]
            if not filename:
                filename = "supplement"
            dest = raw_dir / filename

            if not dest.exists():
                print(f"  Downloading {filename}...", file=sys.stderr)
                if not download_file(url, dest):
                    continue
            else:
                print(f"  Already have {filename}", file=sys.stderr)

            # Skip non-scrapeable files
            if dest.suffix.lower() in (".zip", ".tar", ".gz", ".pdf", ".docx", ".doc"):
                print(f"  Skipping {dest.suffix} file", file=sys.stderr)
                continue

            # Scrape
            out_tsv = VAL_DIR / f"{safe_id}_{dest.stem}.tsv"
            n = scrape_file(dest, "", f"PMID:{pmid}", out_tsv)
            if n > 0:
                print(f"  Scraped {n} MHC strings from {filename}", file=sys.stderr)
                paper_strings += n
                # Load and accumulate
                with open(out_tsv) as f:
                    reader = csv.DictReader(f, delimiter="\t")
                    for row in reader:
                        all_validation_rows.append(row)

        if paper_strings > 0:
            papers_with_data += 1
            total_strings += paper_strings
        else:
            papers_no_mhc += 1

        time.sleep(0.5)  # be polite

    # Write consolidated validation file
    consolidated = VAL_DIR / "all_papers.tsv"
    with open(consolidated, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["raw_string", "expected_species", "source"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(all_validation_rows)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Results:", file=sys.stderr)
    print(f"  Papers processed:    {len(papers)}", file=sys.stderr)
    print(f"  With MHC data:       {papers_with_data}", file=sys.stderr)
    print(f"  No supplementary:    {papers_no_supp}", file=sys.stderr)
    print(f"  No MHC strings:      {papers_no_mhc}", file=sys.stderr)
    print(f"  Total MHC strings:   {total_strings}", file=sys.stderr)
    print(f"  Consolidated file:   {consolidated}", file=sys.stderr)


if __name__ == "__main__":
    main()
