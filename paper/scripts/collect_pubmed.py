#!/usr/bin/env python3
"""
Systematic PubMed search for MHC papers with downloadable allele lists.

Runs one query per taxonomic stratum, retrieves paper metadata,
and outputs a TSV of candidate papers for manual review.

Usage:
    python paper/scripts/collect_pubmed.py --output paper/validation/candidate_papers.tsv
"""

import argparse
import csv
import sys
import time

try:
    from Bio import Entrez
except ImportError:
    print("Requires biopython: pip install biopython", file=sys.stderr)
    sys.exit(1)

Entrez.email = "mhcgnomes-paper@example.com"

# One query per taxonomic stratum, targeting papers with supplementary
# allele data published 2015-2025
STRATA = {
    "human_clinical": (
        '("HLA typing" OR "HLA genotyping") '
        "AND (supplementary OR table) "
        "AND 2015:2025[dp] "
        "NOT review[pt]"
    ),
    "human_population": (
        '("HLA frequency" OR "HLA distribution" OR "allele frequency") '
        "AND population AND HLA "
        "AND 2015:2025[dp] "
        "NOT review[pt]"
    ),
    "nonhuman_primate": (
        "(MHC OR Mamu OR Mafa OR Patr) "
        "AND (macaque OR chimpanzee OR marmoset) "
        "AND (genotyping OR allele) "
        "AND 2015:2025[dp]"
    ),
    "rodent": (
        '(MHC OR "H-2" OR H2) '
        "AND (mouse OR rat OR hamster) "
        "AND (haplotype OR genotyping OR allele) "
        "AND 2015:2025[dp] "
        "NOT review[pt]"
    ),
    "bird": (
        '("MHC diversity" OR "MHC class II" OR "MHC genotyping") '
        "AND (passerine OR raptor OR penguin OR waterfowl OR songbird OR avian) "
        "AND 2018:2025[dp]"
    ),
    "fish": (
        "(MHC) AND (salmonid OR cichlid OR zebrafish OR carp OR teleost) "
        "AND (diversity OR genotyping OR class) "
        "AND 2018:2025[dp]"
    ),
    "reptile_amphibian": (
        "(MHC) AND (turtle OR lizard OR snake OR frog OR amphibian OR reptile) "
        'AND ("class I" OR "class II" OR diversity) '
        "AND 2018:2025[dp]"
    ),
    "livestock": (
        '(MHC OR BoLA OR SLA OR OLA OR ELA) AND (genotyping OR typing OR allele) '
        "AND (cattle OR pig OR sheep OR horse) "
        "AND 2018:2025[dp] "
        "NOT review[pt]"
    ),
    "wildlife_conservation": (
        '("MHC diversity") '
        "AND (endangered OR conservation OR bottleneck OR threatened) "
        "AND 2018:2025[dp]"
    ),
}


def search_pubmed(query, max_results=20):
    """Search PubMed and return PMIDs."""
    try:
        handle = Entrez.esearch(
            db="pubmed", term=query, retmax=max_results, sort="relevance"
        )
        result = Entrez.read(handle)
        handle.close()
        return result["IdList"]
    except Exception as e:
        print(f"  Search failed: {e}", file=sys.stderr)
        return []


def fetch_paper_metadata(pmids):
    """Fetch title, authors, journal, year, DOI for a list of PMIDs."""
    if not pmids:
        return []
    try:
        handle = Entrez.efetch(
            db="pubmed", id=pmids, rettype="xml", retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()
    except Exception as e:
        print(f"  Fetch failed: {e}", file=sys.stderr)
        return []

    papers = []
    for article in records.get("PubmedArticle", []):
        medline = article.get("MedlineCitation", {})
        art = medline.get("Article", {})

        pmid = str(medline.get("PMID", ""))
        title = art.get("ArticleTitle", "")

        # Extract year
        journal = art.get("Journal", {})
        ji = journal.get("JournalIssue", {})
        pd = ji.get("PubDate", {})
        year = pd.get("Year", pd.get("MedlineDate", ""))

        journal_name = journal.get("Title", "")

        # Extract DOI
        doi = ""
        for eid in art.get("EIdList", []):
            if hasattr(eid, "attributes") and eid.attributes.get("EIdType") == "doi":
                doi = str(eid)
        if not doi:
            article_ids = article.get("PubmedData", {}).get("ArticleIdList", [])
            for aid in article_ids:
                if hasattr(aid, "attributes") and aid.attributes.get("IdType") == "doi":
                    doi = str(aid)

        # First author
        author_list = art.get("AuthorList", [])
        first_author = ""
        if author_list:
            a = author_list[0]
            last = a.get("LastName", "")
            init = a.get("Initials", "")
            first_author = f"{last} {init}" if last else ""

        papers.append({
            "pmid": pmid,
            "first_author": first_author,
            "year": year,
            "title": title,
            "journal": journal_name,
            "doi": doi,
        })

    return papers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", default="paper/validation/candidate_papers.tsv"
    )
    parser.add_argument(
        "--max-per-stratum", type=int, default=10,
        help="Max papers to retrieve per stratum"
    )
    args = parser.parse_args()

    all_papers = []

    for stratum, query in STRATA.items():
        print(f"Searching stratum: {stratum}", file=sys.stderr)
        pmids = search_pubmed(query, max_results=args.max_per_stratum)
        print(f"  Found {len(pmids)} papers", file=sys.stderr)

        if pmids:
            papers = fetch_paper_metadata(pmids)
            for p in papers:
                p["stratum"] = stratum
            all_papers.extend(papers)
            time.sleep(0.5)

    print(f"\nTotal: {len(all_papers)} candidate papers", file=sys.stderr)

    with open(args.output, "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stratum", "pmid", "first_author", "year",
                "title", "journal", "doi",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(all_papers)

    print(f"Written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
