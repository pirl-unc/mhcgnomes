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
import xml.etree.ElementTree as ET

try:
    import biotite.database.entrez as entrez
except ImportError:
    print("Requires biotite: pip install biotite", file=sys.stderr)
    sys.exit(1)


class RawEntrezQuery(entrez.Query):
    """Wrap a raw NCBI Entrez query string for biotite.database.entrez.search."""

    def __init__(self, term):
        self.term = term

    def __str__(self):
        return self.term

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
        return entrez.search(RawEntrezQuery(query), "pubmed", number=max_results)
    except Exception as e:
        print(f"  Search failed: {e}", file=sys.stderr)
        return []


def parse_pubmed_xml(xml_text):
    """Parse PubMed efetch XML into a list of paper metadata dictionaries."""
    root = ET.fromstring(xml_text)
    papers = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext("./MedlineCitation/PMID", default="").strip()
        title_elem = article.find("./MedlineCitation/Article/ArticleTitle")
        title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""

        pub_date = article.find("./MedlineCitation/Article/Journal/JournalIssue/PubDate")
        year = ""
        if pub_date is not None:
            year = (
                pub_date.findtext("Year")
                or pub_date.findtext("MedlineDate")
                or ""
            ).strip()

        journal_name = article.findtext(
            "./MedlineCitation/Article/Journal/Title", default=""
        ).strip()

        doi = ""
        for eid in article.findall("./MedlineCitation/Article/ELocationID"):
            if eid.attrib.get("EIdType") == "doi" and eid.text:
                doi = eid.text.strip()
        if not doi:
            for aid in article.findall("./PubmedData/ArticleIdList/ArticleId"):
                if aid.attrib.get("IdType") == "doi" and aid.text:
                    doi = aid.text.strip()

        first_author = ""
        author = article.find("./MedlineCitation/Article/AuthorList/Author")
        if author is not None:
            last = author.findtext("LastName", default="").strip()
            init = author.findtext("Initials", default="").strip()
            first_author = f"{last} {init}".strip() if last else ""

        papers.append(
            {
                "pmid": pmid,
                "first_author": first_author,
                "year": year,
                "title": title,
                "journal": journal_name,
                "doi": doi,
            }
        )
    return papers


def fetch_paper_metadata(pmids):
    """Fetch title, authors, journal, year, DOI for a list of PMIDs."""
    if not pmids:
        return []
    try:
        handle = entrez.fetch_single_file(
            pmids, None, "pubmed", ret_type="xml", ret_mode="xml"
        )
        return parse_pubmed_xml(handle.getvalue())
    except Exception as e:
        print(f"  Fetch failed: {e}", file=sys.stderr)
        return []


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
