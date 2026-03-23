#!/usr/bin/env python3
"""
Generate publication-ready figures for the paper validation corpus.

Usage:
    python paper/scripts/plot_paper_results.py
"""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from paper_analysis import CORPORA, RESULTS_DIR, TSV_FILENAMES, export_summary_tables


PANEL_LABELS = ["A", "B", "C", "D"]
TAXON_COLORS = {
    "Human": "#2f6690",
    "Non-human primate": "#3d8a6d",
    "Cetacean": "#2a9d8f",
    "Other mammal": "#7b5e57",
    "Bird": "#f28e2b",
    "Fish": "#59a14f",
    "Reptile": "#d1495b",
    "Amphibian": "#9c6ade",
    "Other vertebrate": "#8f98a1",
    "Unassigned": "#c8ccd0",
}
CORPUS_COLORS = {key: config["color"] for key, config in CORPORA.items()}
LIGHT_BAR = "#d9dee2"


def refresh_summary_tables():
    export_summary_tables()


def load_table(key):
    return pd.read_csv(RESULTS_DIR / TSV_FILENAMES[key], sep="\t")


def style_axes(ax, panel_label):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#d7d7d7", linewidth=0.8, alpha=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    ax.text(
        -0.12,
        1.05,
        panel_label,
        transform=ax.transAxes,
        fontsize=16,
        fontweight="bold",
        va="top",
        ha="left",
    )


def save_figure(fig, stem):
    for suffix in (".png", ".pdf", ".svg"):
        path = RESULTS_DIR / f"{stem}{suffix}"
        fig.savefig(path, bbox_inches="tight", dpi=300)


def add_rate_labels(ax, frame, total_col="total_strings", parsed_col="parsed_strings"):
    for idx, row in frame.reset_index(drop=True).iterrows():
        ax.text(
            row[total_col] + max(frame[total_col].max() * 0.01, 0.5),
            idx,
            f"{int(row[parsed_col])}/{int(row[total_col])} ({row['parse_rate_pct']:.1f}%)",
            va="center",
            ha="left",
            fontsize=9,
            color="#333333",
        )


def plot_dataset_overview():
    corpus_df = load_table("corpus_summary")
    species_df = load_table("species_summary")
    taxon_df = load_table("taxon_summary")

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    fig, axes = plt.subplots(1, 3, figsize=(16, 8), gridspec_kw={"width_ratios": [1.0, 1.4, 1.0]})

    corpus_order = ["publisher_pmid", "pmc_open_access", "combined"]
    corpus_panel = corpus_df.set_index("corpus").loc[corpus_order].reset_index()
    y_positions = range(len(corpus_panel))
    axes[0].barh(y_positions, corpus_panel["total_strings"], color=LIGHT_BAR, height=0.7)
    axes[0].barh(
        y_positions,
        corpus_panel["parsed_strings"],
        color=[CORPUS_COLORS[key] for key in corpus_panel["corpus"]],
        height=0.45,
    )
    axes[0].set_yticks(list(y_positions))
    axes[0].set_yticklabels(corpus_panel["corpus_label"])
    axes[0].invert_yaxis()
    axes[0].set_xlabel("Extracted paper strings")
    axes[0].set_title("Corpus size and parse yield")
    add_rate_labels(axes[0], corpus_panel)
    style_axes(axes[0], PANEL_LABELS[0])

    species_panel = species_df[
        (species_df["corpus"] == "combined") & (species_df["species"] != "Unassigned")
    ].head(12)
    y_positions = range(len(species_panel))
    axes[1].barh(y_positions, species_panel["total_strings"], color=LIGHT_BAR, height=0.7)
    axes[1].barh(
        y_positions,
        species_panel["parsed_strings"],
        color=[TAXON_COLORS.get(taxon, "#777777") for taxon in species_panel["major_taxon"]],
        height=0.45,
    )
    axes[1].set_yticks(list(y_positions))
    axes[1].set_yticklabels(species_panel["species"])
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Strings")
    axes[1].set_title("Top inferred species")
    add_rate_labels(axes[1], species_panel)
    style_axes(axes[1], PANEL_LABELS[1])

    taxon_panel = taxon_df[taxon_df["corpus"] == "combined"]
    y_positions = range(len(taxon_panel))
    axes[2].barh(y_positions, taxon_panel["total_strings"], color=LIGHT_BAR, height=0.7)
    axes[2].barh(
        y_positions,
        taxon_panel["parsed_strings"],
        color=[TAXON_COLORS.get(taxon, "#777777") for taxon in taxon_panel["major_taxon"]],
        height=0.45,
    )
    axes[2].set_yticks(list(y_positions))
    axes[2].set_yticklabels(taxon_panel["major_taxon"])
    axes[2].invert_yaxis()
    axes[2].set_xlabel("Strings")
    axes[2].set_title("Taxonomic composition")
    add_rate_labels(axes[2], taxon_panel)
    style_axes(axes[2], PANEL_LABELS[2])

    fig.suptitle("Paper validation corpus overview", fontsize=18, fontweight="bold", y=1.02)
    fig.tight_layout()
    save_figure(fig, "paper_dataset_overview")
    plt.close(fig)


def plot_parser_performance():
    species_df = load_table("species_summary")
    source_df = load_table("source_summary")
    failure_df = load_table("failure_mode_summary")
    round_trip_df = load_table("round_trip_summary")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12), gridspec_kw={"height_ratios": [1.2, 1.0]})

    source_panel = source_df[
        (source_df["corpus"] == "combined") & (source_df["total_strings"] >= 10)
    ].sort_values(["total_strings", "parse_rate_pct"], ascending=[False, False]).head(15)
    y_positions = range(len(source_panel))
    axes[0, 0].barh(
        y_positions,
        source_panel["parse_rate_pct"],
        color=[
            CORPUS_COLORS["pmc_open_access"] if source.startswith("PMC:") else CORPUS_COLORS["publisher_pmid"]
            for source in source_panel["source"]
        ],
        height=0.65,
    )
    axes[0, 0].set_yticks(list(y_positions))
    axes[0, 0].set_yticklabels(source_panel["source"])
    axes[0, 0].invert_yaxis()
    axes[0, 0].set_xlim(0, 105)
    axes[0, 0].set_xlabel("Parse rate (%)")
    axes[0, 0].set_title("Source-level parse rates (sources with N ≥ 10)")
    for idx, row in source_panel.reset_index(drop=True).iterrows():
        axes[0, 0].text(
            min(row["parse_rate_pct"] + 1.5, 101.5),
            idx,
            f"{int(row['parsed_strings'])}/{int(row['total_strings'])}",
            va="center",
            ha="left",
            fontsize=9,
        )
    style_axes(axes[0, 0], PANEL_LABELS[0])

    species_panel = species_df[
        (species_df["corpus"] == "combined")
        & (species_df["species"] != "Unassigned")
        & (species_df["total_strings"] >= 10)
    ].sort_values(["total_strings", "parse_rate_pct"], ascending=[False, False]).head(15)
    y_positions = range(len(species_panel))
    axes[0, 1].barh(
        y_positions,
        species_panel["parse_rate_pct"],
        color=[TAXON_COLORS.get(taxon, "#777777") for taxon in species_panel["major_taxon"]],
        height=0.65,
    )
    axes[0, 1].set_yticks(list(y_positions))
    axes[0, 1].set_yticklabels(species_panel["species"])
    axes[0, 1].invert_yaxis()
    axes[0, 1].set_xlim(0, 105)
    axes[0, 1].set_xlabel("Parse rate (%)")
    axes[0, 1].set_title("Species-level parse rates (species with N ≥ 10)")
    for idx, row in species_panel.reset_index(drop=True).iterrows():
        axes[0, 1].text(
            min(row["parse_rate_pct"] + 1.5, 101.5),
            idx,
            f"{int(row['parsed_strings'])}/{int(row['total_strings'])}",
            va="center",
            ha="left",
            fontsize=9,
        )
    style_axes(axes[0, 1], PANEL_LABELS[1])

    failure_panel = failure_df[failure_df["corpus"] == "combined"].copy()
    y_positions = range(len(failure_panel))
    axes[1, 0].barh(y_positions, failure_panel["pct_of_failures"], color="#b24c63", height=0.65)
    axes[1, 0].set_yticks(list(y_positions))
    axes[1, 0].set_yticklabels(failure_panel["failure_mode"])
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_xlabel("Share of failed strings (%)")
    axes[1, 0].set_title("Failure mode distribution")
    for idx, row in failure_panel.reset_index(drop=True).iterrows():
        axes[1, 0].text(
            row["pct_of_failures"] + 0.8,
            idx,
            f"{int(row['count'])}",
            va="center",
            ha="left",
            fontsize=9,
        )
    style_axes(axes[1, 0], PANEL_LABELS[2])

    axes[1, 1].axis("off")
    axes[1, 1].text(
        0.0,
        1.03,
        PANEL_LABELS[3],
        transform=axes[1, 1].transAxes,
        fontsize=16,
        fontweight="bold",
        va="top",
        ha="left",
    )
    axes[1, 1].set_title("Representative failures", loc="left", fontsize=13, pad=12)

    blocks = []
    for _, row in failure_panel.iterrows():
        examples = [row["example_1"], row["example_2"], row["example_3"]]
        examples = [example for example in examples if isinstance(example, str) and example]
        wrapped = ", ".join(examples)
        blocks.append(
            f"{row['failure_mode']} ({int(row['count'])})\n"
            + textwrap.fill(wrapped, width=46, subsequent_indent="  ")
        )

    if not round_trip_df.empty:
        round_trip_note = (
            "\n\nRound-trip normalization issue:\n"
            + textwrap.fill(
                ", ".join(round_trip_df["raw_string"].tolist()),
                width=46,
                subsequent_indent="  ",
            )
        )
    else:
        round_trip_note = ""

    axes[1, 1].text(
        0.0,
        0.96,
        "\n\n".join(blocks) + round_trip_note,
        va="top",
        ha="left",
        fontsize=10,
        family="DejaVu Sans Mono",
    )

    fig.suptitle("Paper parse rates and failure modes", fontsize=18, fontweight="bold", y=1.01)
    fig.tight_layout()
    save_figure(fig, "paper_parse_failures")
    plt.close(fig)


def main():
    refresh_summary_tables()
    plot_dataset_overview()
    plot_parser_performance()
    print("Wrote figures to paper/results/")


if __name__ == "__main__":
    main()
