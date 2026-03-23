#!/usr/bin/env python3
"""
Export summary tables for the paper validation corpus.

Usage:
    python paper/scripts/build_paper_results.py
"""

from paper_analysis import export_summary_tables, write_markdown_summary


def main():
    summary_tables = export_summary_tables()
    markdown_path = write_markdown_summary(summary_tables)
    print(f"Wrote summary tables to paper/results/")
    print(f"Wrote markdown summary to {markdown_path}")


if __name__ == "__main__":
    main()
