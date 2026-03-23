#!/usr/bin/env python3
"""
Collect MHC allele strings from open-access papers, targeting species diversity.

v2: Focuses on PMC open access, adds species-targeted queries, and
generates a manual review set for each paper.

Usage:
    python paper/scripts/collect_all_v2.py
"""

import csv
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

try:
    from Bio import Entrez
except ImportError:
    print("Requires biopython: pip install biopython", file=sys.stderr)
    sys.exit(1)

Entrez.email = "mhcgnomes-paper@example.com"

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "paper" / "raw"
VAL_DIR = ROOT / "paper" / "validation"
REVIEW_DIR = ROOT / "paper" / "review"
SCRAPE_SCRIPT = ROOT / "paper" / "scripts" / "scrape_paper.py"
TITLE_KEYWORD_PATTERN = re.compile(
    r"\b("
    r"mhc|major histocompatibility complex|immunogenetic\w*|hla|bola|sla|dla|ela|fla|"
    r"mamu|mafa|patr|gogo|papa|drb\d*|dqb\d*|dqa\d*|dpa\d*|dpb\d*|"
    r"dab\d*|bf\d*|blb\d*|uaa\d*|uba\d*|mhcy\d*"
    r")\b",
    re.IGNORECASE,
)

# Open-access focused queries targeting species diversity.
# "open access"[filter] restricts to PMC OA subset.
QUERIES = {
    # ── Birds ──
    "bird_passerine": '"MHC class II" AND (passerine OR warbler OR finch OR tit OR sparrow) AND allele AND 2018:2025[dp]',
    "bird_raptor": '"MHC" AND (raptor OR eagle OR falcon OR owl OR hawk) AND (diversity OR allele) AND 2018:2025[dp]',
    "bird_seabird": '"MHC" AND (penguin OR petrel OR albatross OR gull OR tern) AND (diversity OR allele) AND 2018:2025[dp]',
    "bird_galliform": '("MHC" OR "BLB" OR "BF") AND (chicken OR turkey OR quail OR pheasant OR grouse) AND (allele OR haplotype) AND 2018:2025[dp]',
    "bird_waterfowl": '"MHC" AND (duck OR goose OR swan) AND (diversity OR allele) AND 2018:2025[dp]',
    # ── Fish ──
    "fish_salmonid": '("MHC" OR "UBA" OR "DAB") AND (salmon OR trout OR salmonid) AND (allele OR genotyping) AND 2018:2025[dp]',
    "fish_cichlid": '"MHC" AND cichlid AND (diversity OR allele) AND 2018:2025[dp]',
    "fish_other": '"MHC" AND (carp OR zebrafish OR tilapia OR cod OR stickleback OR catfish) AND (allele OR diversity) AND 2018:2025[dp]',
    # ── Reptiles & amphibians ──
    "reptile_turtle": '"MHC" AND (turtle OR tortoise) AND (diversity OR allele) AND 2015:2025[dp]',
    "reptile_lizard_snake": '"MHC" AND (lizard OR snake OR iguana OR gecko) AND (diversity OR allele) AND 2015:2025[dp]',
    "reptile_croc": '"MHC" AND (crocodile OR alligator OR caiman) AND 2015:2025[dp]',
    "amphibian": '"MHC" AND (frog OR toad OR salamander OR newt OR Xenopus) AND (diversity OR allele) AND 2018:2025[dp]',
    # ── Mammals (non-model) ──
    "mammal_bat": '"MHC" AND (bat OR chiroptera OR Myotis) AND (diversity OR allele) AND 2018:2025[dp]',
    "mammal_marsupial": '"MHC" AND (marsupial OR koala OR possum OR wallaby OR devil) AND (diversity OR allele) AND 2015:2025[dp]',
    "mammal_marine": '"MHC" AND (whale OR dolphin OR seal OR pinniped) AND (diversity OR allele) AND 2018:2025[dp]',
    "mammal_carnivore": '("MHC" OR "DLA" OR "FLA") AND (wolf OR cheetah OR leopard OR bear) AND (diversity OR allele) AND 2018:2025[dp]',
    "mammal_ungulate": '("MHC" OR "BoLA" OR "SLA" OR "OLA" OR "ELA") AND (cattle OR pig OR sheep OR horse OR deer) AND (genotyping OR allele) AND 2018:2025[dp]',
    "mammal_primate": '("MHC" OR "Mamu" OR "Mafa") AND (macaque OR chimpanzee OR gorilla OR marmoset) AND (genotyping OR allele) AND 2018:2025[dp]',
    "mammal_rodent": '("MHC" OR "H-2") AND (hamster OR vole OR squirrel OR guinea) AND diversity AND 2018:2025[dp]',
    # ── Conservation ──
    "conservation": '"MHC diversity" AND (endangered OR conservation OR bottleneck) AND allele AND 2018:2025[dp]',
    # ── Human (population) ──
    "human_population": '"HLA" AND "allele frequency" AND population AND genotyping AND 2020:2025[dp]',
    # ── Shark ──
    "shark": '"MHC" AND (shark OR elasmobranch) AND 2010:2025[dp]',
}



def search_pubmed(query, max_results=15):
    try:
        handle = Entrez.esearch(
            db="pmc", term=query, retmax=max_results, sort="relevance"
        )
        result = Entrez.read(handle)
        handle.close()
        return result["IdList"]
    except Exception as e:
        print(f"  Search failed: {e}", file=sys.stderr)
        return []


def fetch_paper_metadata(pmc_ids):
    """Fetch metadata for PMC IDs. Returns basic info from PMC summaries."""
    if not pmc_ids:
        return []
    papers = []
    try:
        handle = Entrez.esummary(db="pmc", id=",".join(pmc_ids))
        records = Entrez.read(handle)
        handle.close()
        for rec in records:
            papers.append({
                "pmid": str(rec.get("Id", "")),
                "first_author": str(rec.get("AuthorList", [""])[0]) if rec.get("AuthorList") else "",
                "year": str(rec.get("PubDate", ""))[:4],
                "title": str(rec.get("Title", "")),
                "journal": str(rec.get("FullJournalName", rec.get("Source", ""))),
                "doi": str(rec.get("DOI", "")),
            })
    except Exception as e:
        print(f"  Metadata fetch failed: {e}", file=sys.stderr)
        # Fall back to just using IDs
        for pmc_id in pmc_ids:
            papers.append({
                "pmid": pmc_id, "first_author": "", "year": "",
                "title": "", "journal": "", "doi": "",
            })
    return papers


def title_looks_mhc_related(title):
    """Drop obvious off-target papers that only matched broad search recall."""
    if not title:
        return True
    return bool(TITLE_KEYWORD_PATTERN.search(title))


def deduplicate_validation_rows(rows):
    seen = set()
    deduped = []
    for row in rows:
        key = (
            row.get("raw_string", ""),
            row.get("expected_species", ""),
            row.get("source", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def pmid_to_pmc(pmid):
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


def download_pmc_package(pmc_id, raw_dir):
    """Download PMC OA package and extract supplementary files.

    Returns list of extracted file paths.
    """
    import tarfile

    # Get FTP URL from OA API
    try:
        oa_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC{pmc_id}"
        req = urllib.request.Request(oa_url, headers={"User-Agent": "mhcgnomes-paper/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode()
    except Exception:
        return []

    # Extract FTP URL
    m = re.search(r'href="(ftp://[^"]+\.tar\.gz)"', text)
    if not m:
        # Try HTTPS fallback
        m = re.search(r'href="(https?://[^"]+\.tar\.gz)"', text)
    if not m:
        return []

    pkg_url = m.group(1)
    # Convert ftp to https for reliability
    pkg_url = pkg_url.replace("ftp://ftp.ncbi.nlm.nih.gov/", "https://ftp.ncbi.nlm.nih.gov/")

    # Download the package
    pkg_path = raw_dir / f"PMC{pmc_id}.tar.gz"
    if not pkg_path.exists():
        try:
            req = urllib.request.Request(pkg_url, headers={"User-Agent": "mhcgnomes-paper/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(pkg_path, "wb") as f:
                    f.write(resp.read())
        except Exception as e:
            print(f"    Download failed: {e}", file=sys.stderr)
            return []

    # Extract supplementary files
    extracted = []
    try:
        with tarfile.open(pkg_path, "r:gz") as tar:
            for member in tar.getmembers():
                name_lower = member.name.lower()
                if any(name_lower.endswith(ext) for ext in
                       [".xlsx", ".xls", ".csv", ".tsv", ".txt", ".docx"]):
                    # Extract to raw_dir
                    member.name = Path(member.name).name  # flatten path
                    tar.extract(member, raw_dir)
                    extracted.append(raw_dir / member.name)
    except Exception as e:
        print(f"    Extract failed: {e}", file=sys.stderr)

    return extracted


def download_file(url, dest):
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
    try:
        result = subprocess.run(
            [
                sys.executable, str(SCRAPE_SCRIPT),
                "--input", str(filepath),
                "--species", species,
                "--source", source,
                "--output", str(output),
            ],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            return sum(1 for _ in open(output)) - 1
    except Exception:
        pass
    return 0


def generate_review_file(scrape_tsv, review_path):
    """Create a review TSV with parsed/unparsed status for manual audit."""
    try:
        from mhcgnomes import parse as mhc_parse
    except ImportError:
        return

    rows = []
    with open(scrape_tsv) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            raw = row["raw_string"]
            result = mhc_parse(raw, raise_on_error=False)
            parsed = result is not None
            rows.append({
                "raw_string": raw,
                "parsed": "yes" if parsed else "no",
                "parsed_as": str(result) if parsed else "",
                "result_type": type(result).__name__ if parsed else "",
                "species": result.species.name if parsed and hasattr(result, "species") and result.species else "",
                "correct": "",  # for manual review
                "notes": "",    # for manual review
                "source": row.get("source", ""),
            })

    with open(review_path, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["raw_string", "parsed", "parsed_as", "result_type",
                         "species", "correct", "notes", "source"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Run all queries
    all_pmids = set()
    stratum_papers = {}

    for stratum, query in QUERIES.items():
        print(f"Searching: {stratum}", file=sys.stderr)
        pmids = search_pubmed(query, max_results=15)
        print(f"  Found {len(pmids)} papers", file=sys.stderr)
        new_pmids = [p for p in pmids if p not in all_pmids]
        all_pmids.update(pmids)

        if new_pmids:
            papers = fetch_paper_metadata(new_pmids)
            kept = [p for p in papers if title_looks_mhc_related(p.get("title", ""))]
            filtered = len(papers) - len(kept)
            if filtered:
                print(f"  Filtered {filtered} off-target titles", file=sys.stderr)
            for p in papers:
                p["stratum"] = stratum
            stratum_papers[stratum] = kept
        time.sleep(0.4)

    # Save expanded candidate list
    all_papers = []
    for papers in stratum_papers.values():
        all_papers.extend(papers)

    candidates_path = VAL_DIR / "candidate_papers_v2.tsv"
    with open(candidates_path, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["stratum", "pmid", "first_author", "year",
                         "title", "journal", "doi"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(all_papers)
    print(f"\n{len(all_papers)} candidate papers → {candidates_path}\n", file=sys.stderr)

    # Step 2: Process each paper
    total_strings = 0
    papers_with_data = 0
    consolidated_rows = []

    for i, paper in enumerate(all_papers):
        pmid = paper["pmid"]
        stratum = paper["stratum"]
        title = paper.get("title", "")[:60]

        print(f"[{i+1}/{len(all_papers)}] PMC{pmid} ({stratum}) {title}...", file=sys.stderr)

        safe_id = f"PMC_{pmid}"
        raw_dir = RAW_DIR / safe_id
        raw_dir.mkdir(parents=True, exist_ok=True)

        pmc_id = pmid  # Already a PMC ID from PMC search

        # Download OA package and extract supplementary files
        extracted = download_pmc_package(pmc_id, raw_dir)
        if not extracted:
            time.sleep(0.3)
            continue

        print(f"  {len(extracted)} supplementary files extracted", file=sys.stderr)

        paper_strings = 0
        paper_tsvs = []

        for dest in extracted:
            out_tsv = VAL_DIR / f"{safe_id}_{dest.stem}.tsv"
            n = scrape_file(dest, "", f"PMC:{pmid}", out_tsv)
            if n > 0:
                print(f"  {n} strings from {dest.name}", file=sys.stderr)
                paper_strings += n
                paper_tsvs.append(out_tsv)
                with open(out_tsv) as f:
                    reader = csv.DictReader(f, delimiter="\t")
                    for row in reader:
                        consolidated_rows.append(row)

        if paper_strings > 0:
            papers_with_data += 1
            total_strings += paper_strings

            # Generate review file for this paper
            # Merge all TSVs for this paper into one review file
            review_path = REVIEW_DIR / f"{safe_id}_review.tsv"
            merged_tsv = VAL_DIR / f"{safe_id}_merged.tsv"
            merged_rows = []
            for tsv in paper_tsvs:
                with open(tsv) as tf:
                    reader = csv.DictReader(tf, delimiter="\t")
                    merged_rows.extend(reader)
            merged_rows = deduplicate_validation_rows(merged_rows)

            with open(merged_tsv, "w") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["raw_string", "expected_species", "source"],
                    delimiter="\t",
                )
                writer.writeheader()
                writer.writerows(merged_rows)

            generate_review_file(merged_tsv, review_path)
            review_lines = sum(1 for _ in open(review_path)) - 1
            print(f"  Review file: {review_path} ({review_lines} entries)", file=sys.stderr)

        time.sleep(0.5)

    # Write consolidated file
    consolidated = VAL_DIR / "all_papers_v2.tsv"
    with open(consolidated, "w") as f:
        writer = csv.DictWriter(
            f, fieldnames=["raw_string", "expected_species", "source"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(deduplicate_validation_rows(consolidated_rows))

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Papers with data:  {papers_with_data}", file=sys.stderr)
    print(f"Total strings:     {total_strings}", file=sys.stderr)
    print(f"Consolidated:      {consolidated}", file=sys.stderr)
    print(f"Review files:      {REVIEW_DIR}/", file=sys.stderr)


if __name__ == "__main__":
    main()
