#!/usr/bin/env bash
set -euo pipefail
#
# Batch-download and scrape supplementary data from candidate papers.
#
# Usage:
#   # Download a paper's supplementary file and scrape it
#   ./paper/scripts/batch_collect.sh add PMID:12345678 "Parus major" \
#       https://example.com/supp_table_S1.xlsx
#
#   # Scrape an already-downloaded file
#   ./paper/scripts/batch_collect.sh scrape PMID:12345678 "Gallus gallus" \
#       paper/raw/PMID_12345678/table_S1.xlsx
#
#   # Re-run all scraping (after updating scrape_paper.py)
#   ./paper/scripts/batch_collect.sh rescrape
#
#   # Evaluate all collected validation data
#   ./paper/scripts/batch_collect.sh eval

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RAW_DIR="$ROOT/paper/raw"
VAL_DIR="$ROOT/paper/validation"

cmd="${1:-help}"
shift || true

case "$cmd" in
    add)
        # Download a supplementary file and scrape it
        SOURCE="${1:?Usage: batch_collect.sh add SOURCE SPECIES URL}"
        SPECIES="${2:?}"
        URL="${3:?}"

        SAFE_SOURCE="$(echo "$SOURCE" | tr ':/' '_')"
        mkdir -p "$RAW_DIR/$SAFE_SOURCE"

        FILENAME="$(basename "$URL")"
        DEST="$RAW_DIR/$SAFE_SOURCE/$FILENAME"

        echo "Downloading $URL → $DEST"
        curl -sSfL "$URL" -o "$DEST"

        echo "Scraping $DEST"
        python "$ROOT/paper/scripts/scrape_paper.py" \
            --input "$DEST" \
            --species "$SPECIES" \
            --source "$SOURCE" \
            --output "$VAL_DIR/${SAFE_SOURCE}.tsv"

        echo "Done: $VAL_DIR/${SAFE_SOURCE}.tsv"
        ;;

    scrape)
        # Scrape an already-downloaded file
        SOURCE="${1:?Usage: batch_collect.sh scrape SOURCE SPECIES FILE}"
        SPECIES="${2:?}"
        FILE="${3:?}"

        SAFE_SOURCE="$(echo "$SOURCE" | tr ':/' '_')"

        echo "Scraping $FILE"
        python "$ROOT/paper/scripts/scrape_paper.py" \
            --input "$FILE" \
            --species "$SPECIES" \
            --source "$SOURCE" \
            --output "$VAL_DIR/${SAFE_SOURCE}.tsv"

        echo "Done: $VAL_DIR/${SAFE_SOURCE}.tsv"
        ;;

    rescrape)
        # Re-scrape all raw directories
        for dir in "$RAW_DIR"/*/; do
            [ -d "$dir" ] || continue
            SAFE_SOURCE="$(basename "$dir")"

            # Read species from first line of existing TSV if available
            SPECIES=""
            TSV="$VAL_DIR/${SAFE_SOURCE}.tsv"
            if [ -f "$TSV" ]; then
                SPECIES="$(tail -1 "$TSV" | cut -f2)"
            fi

            # Reconstruct source from dirname
            SOURCE="$(echo "$SAFE_SOURCE" | sed 's/_/:/; s/_/\//')"

            echo "Re-scraping $dir → $TSV"
            python "$ROOT/paper/scripts/scrape_paper.py" \
                --input-dir "$dir" \
                --species "${SPECIES:-}" \
                --source "$SOURCE" \
                --output "$TSV"
        done
        echo "Done."
        ;;

    eval)
        # Evaluate all validation TSVs
        echo "Evaluating all validation data..."
        python "$ROOT/paper/scripts/evaluate.py" "$VAL_DIR"/*.tsv
        ;;

    help|*)
        cat <<'USAGE'
Usage:
  batch_collect.sh add SOURCE SPECIES URL     Download and scrape
  batch_collect.sh scrape SOURCE SPECIES FILE  Scrape local file
  batch_collect.sh rescrape                    Re-scrape all raw dirs
  batch_collect.sh eval                        Evaluate all validation data

Examples:
  ./paper/scripts/batch_collect.sh add "PMID:34567890" "Parus major" \
      https://journals.plos.org/plosone/article/file?id=info:doi/10.1371/journal.pone.0234567.s001&type=supplementary

  ./paper/scripts/batch_collect.sh eval
USAGE
        ;;
esac
