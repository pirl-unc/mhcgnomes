"""
Gradio web frontend for mhcgnomes — MHC nomenclature parsing.

Run with: python app.py
"""

import json

import gradio as gr
import mhcgnomes

# ---------------------------------------------------------------------------
# Tool-specific logic (swap this section for a different tool)
# ---------------------------------------------------------------------------

TOOL_NAME = "mhcgnomes"
TOOL_DESCRIPTION = "Parse any MHC nomenclature into structured, normalized form."
TOOL_URL = "https://github.com/openvax/mhcgnomes"

EXAMPLES = [
    "HLA-A*02:01",
    "A0201",
    "HLA-A2",
    "A01 supertype",
    "DRB1*01:01",
    "DQA1*05:01/DQB1*02:01",
    "HLA-DR",
    "H2-Kb",
    "H2-b",
    "Mamu-A*01:01",
    "mouse class I",
    "HLA-B*08:01 N80I mutant",
]

COLUMNS = ["Input", "Type", "Normalized", "Compact", "Species", "Gene", "MHC Class"]


def _get_species_name(result):
    sp = getattr(result, "species", None)
    if sp is None:
        return ""
    return f"{sp.common_name} ({sp.name})"


def _get_mhc_class(result):
    cls = getattr(result, "mhc_class", None)
    if cls:
        return cls
    rep = getattr(result, "representative", None)
    if rep:
        cls = getattr(rep, "mhc_class", None)
        if cls:
            return cls
    alleles = getattr(result, "alleles", None)
    if alleles:
        classes = {getattr(a, "mhc_class", None) for a in alleles} - {None}
        if len(classes) == 1:
            return classes.pop()
        if classes:
            return "/".join(sorted(classes))
    return ""


def parse_one(name, default_species="HLA", infer_class2=False, max_fields=None):
    """Parse a single MHC name. Returns (row_dict, detail_dict)."""
    species_arg = default_species.strip() if default_species and default_species.strip() else "HLA"
    max_f = int(max_fields) if max_fields else None
    try:
        result = mhcgnomes.parse(
            name,
            default_species=species_arg,
            infer_class2_pairing=infer_class2,
            max_allele_fields=max_f,
            raise_on_error=True,
        )
        result_type = type(result).__name__
        normalized = result.to_string()
        try:
            compact = result.compact_string()
        except Exception:
            compact = normalized
        try:
            record = result.to_record()
        except NotImplementedError:
            record = {"normalized": normalized}

        row = {
            "Input": name,
            "Type": result_type,
            "Normalized": normalized,
            "Compact": compact,
            "Species": _get_species_name(result),
            "Gene": getattr(getattr(result, "gene", None), "name", ""),
            "MHC Class": _get_mhc_class(result),
        }
        detail = {"input": name, "type": result_type, "normalized": normalized, **record}
        return row, detail
    except mhcgnomes.ParseError as e:
        row = dict.fromkeys(COLUMNS, "")
        row["Input"] = name
        row["Type"] = "parse error"
        row["Normalized"] = str(e)
        return row, {"input": name, "error": str(e)}


# ---------------------------------------------------------------------------
# UI logic (generic — reusable across tools)
# ---------------------------------------------------------------------------


def _rows_to_html(rows):
    """Render result rows as a clean HTML table."""
    if not rows:
        return ""
    header = "".join(f"<th>{c}</th>" for c in COLUMNS)
    body = ""
    for row in rows:
        cells = "".join(
            f'<td class="{"error" if row.get("Type") == "parse error" else ""}">'
            f"{row.get(c, '')}</td>"
            for c in COLUMNS
        )
        body += f"<tr>{cells}</tr>"
    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def run_parse(text, file, default_species, infer_class2, max_fields):
    """Main handler: parse text input or uploaded file contents."""
    if file is not None:
        with open(file, "r") as f:
            text = f.read()
    if not text or not text.strip():
        return "", ""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    rows, details = [], []
    for line in lines:
        row, detail = parse_one(line, default_species, infer_class2, max_fields)
        rows.append(row)
        details.append(detail)
    j = json.dumps(details[0] if len(details) == 1 else details, indent=2, default=str)
    return _rows_to_html(rows), j


def run_example(example_text):
    """Click an example: populate input + parse it immediately."""
    row, detail = parse_one(example_text)
    j = json.dumps(detail, indent=2, default=str)
    return example_text, _rows_to_html([row]), j


CSS = """
/* Layout */
.gradio-container { max-width: 1100px !important; margin: auto; }

/* Typography: proportional for chrome, mono for data */
.gradio-container { font-family: -apple-system, "Segoe UI", Roboto, sans-serif !important; }
textarea, code, pre, td, th, .prose table {
    font-family: "SF Mono", Menlo, Consolas, monospace !important;
}

/* Header */
.tool-header { margin-bottom: 12px; }
.tool-header h1 {
    font-size: 1.5em !important; font-weight: 700 !important;
    margin: 0 !important; letter-spacing: -0.02em;
}
.tool-header p {
    color: #666; font-size: 0.9em; margin: 2px 0 0 0;
}
.tool-header a { color: #555; text-decoration: none; font-size: 0.8em; }
.tool-header a:hover { text-decoration: underline; }
.tool-header hr { border: none; border-top: 2px solid #1a1a2e; margin: 10px 0 0 0; }

/* Input area */
.main-input textarea {
    font-size: 0.95em !important;
    border: 2px solid #d0d0d0 !important;
    border-radius: 4px !important;
}
.main-input textarea:focus {
    border-color: #1a1a2e !important;
}

/* Examples */
.examples-label { font-size: 0.78em; color: #888; margin: 6px 0 3px 2px; }
.examples-row {
    flex-wrap: wrap !important; gap: 5px !important;
    margin-bottom: 8px !important;
}
.examples-row .block {
    flex: none !important; min-width: 0 !important; width: auto !important;
}
.examples-row button {
    font-family: "SF Mono", Menlo, Consolas, monospace !important;
    font-size: 0.78em !important;
    padding: 2px 7px !important;
    border-radius: 3px !important;
    border: 1px solid #d0d0d0 !important;
    background: #fafafa !important;
    color: #333 !important;
    cursor: pointer !important;
}
.examples-row button:hover {
    background: #1a1a2e !important;
    color: #fff !important;
    border-color: #1a1a2e !important;
}

/* Results table */
.results-area table {
    font-family: "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.82em; border-collapse: collapse; width: 100%;
}
.results-area th {
    background: #1a1a2e; color: #e0e0e0;
    padding: 7px 12px; text-align: left;
    font-weight: 600; font-size: 0.85em;
    letter-spacing: 0.03em; text-transform: uppercase;
}
.results-area td {
    padding: 5px 12px; border-bottom: 1px solid #eee;
}
.results-area tr:nth-child(even) td { background: #f8f8fb; }
.results-area td.error { color: #a33; }

/* Options sidebar */
.options-panel { font-size: 0.88em; }
.options-panel label { font-size: 0.85em !important; }

/* Buttons */
button.primary {
    background: #1a1a2e !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
}

/* JSON accordion */
.json-accordion { margin-top: 4px; }
"""


with gr.Blocks(title=TOOL_NAME) as app:

    # Header
    gr.HTML(
        f'<div class="tool-header">'
        f"<h1>{TOOL_NAME}</h1>"
        f"<p>{TOOL_DESCRIPTION}</p>"
        f'<a href="{TOOL_URL}">{TOOL_URL}</a>'
        f"<hr></div>"
    )

    # Examples
    gr.HTML('<div class="examples-label">EXAMPLES &mdash; click to try</div>')
    with gr.Row(elem_classes=["examples-row"]):
        example_buttons = []
        for ex in EXAMPLES:
            ebtn = gr.Button(ex, size="sm", variant="secondary")
            example_buttons.append(ebtn)

    # Main input row
    with gr.Row():
        with gr.Column(scale=4):
            text_input = gr.Textbox(
                show_label=False,
                placeholder="Type or paste allele names, one per line",
                lines=4,
                elem_classes=["main-input"],
            )
            with gr.Row():
                file_input = gr.File(
                    label="or drop a file (.txt, .csv, .tsv)",
                    file_types=[".txt", ".csv", ".tsv"],
                    type="filepath",
                )
                parse_btn = gr.Button("Parse", variant="primary", size="lg")

        with gr.Column(scale=1, elem_classes=["options-panel"]):
            gr.HTML('<div style="font-size:0.78em; color:#888; margin-bottom:4px">OPTIONS</div>')
            default_species = gr.Textbox(label="Default species", value="HLA")
            infer_class2 = gr.Checkbox(label="Infer Class II pairing", value=False)
            max_fields = gr.Number(label="Max allele fields", value=None, precision=0)

    # Results — use HTML table rendering instead of Dataframe widget
    results_html = gr.HTML(value="", elem_classes=["results-area"])
    with gr.Accordion("JSON", open=False, elem_classes=["json-accordion"]):
        json_output = gr.Code(show_label=False, language="json")

    # --- Wire events ---

    parse_inputs = [text_input, file_input, default_species, infer_class2, max_fields]
    parse_outputs = [results_html, json_output]

    parse_btn.click(fn=run_parse, inputs=parse_inputs, outputs=parse_outputs)
    text_input.submit(fn=run_parse, inputs=parse_inputs, outputs=parse_outputs)

    # Example buttons: populate input + show result in one click
    for ebtn, ex in zip(example_buttons, EXAMPLES):
        ebtn.click(
            fn=run_example,
            inputs=[gr.State(ex)],
            outputs=[text_input, results_html, json_output],
        )


if __name__ == "__main__":
    app.launch(css=CSS)
