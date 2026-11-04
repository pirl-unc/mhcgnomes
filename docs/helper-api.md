# Public helper APIs

These helpers are supported at the module or class paths below. Use `parse`
for complete parsing policy. Lower-level helpers have deliberately narrower
contracts; they do not establish that an allele or species is biologically valid.
Direct tests and internal callers use the same public names.

## Inputs and table rows

- `mhcgnomes.input_validation.validate_mhc_input(value, raise_on_error=True)`
  returns `True` for strings. Scalar missing inputs return `False` in tolerant
  mode or raise `ParseError`; other types raise `TypeError`. It does not coerce
  strings or tokenize them.
- `mhcgnomes.parse_outcome_to_row(raw_input, outcome)` accepts a `Result`,
  `ParseError`, or `None`. It returns a new dictionary with `input`, `type`,
  `normalized`, `compact`, `species`, `gene_name`, `mhc_class`, `properties`,
  and `error`, plus available `to_record()` fields. `gene_name` is short;
  legacy `gene` fields retain their full identifier. The input is preserved.
  A successful Haplotype still has a row without a record schema. Unsupported
  outcome types raise `TypeError`; serialization errors propagate except for
  `NotImplementedError` from the optional record schema.
- `mhcgnomes.cli.outcome_to_cli_row(raw_input, outcome)` projects that row into
  the CLI's existing eight string columns, using `gene_name` for its `gene`
  display. It has the same outcome/error contract.

## Parser building blocks

| Public API | Inputs and result | Scope |
|---|---|---|
| `mhcgnomes.parser.blank_locus_gene_name(member)` | String to gene-name string or `None` | Recognizes exactly one star and a case-insensitive `Blank`/`null` field; trims whitespace. Does not look up the gene. |
| `Parser.find_matching_name_and_parse_alleles(query_name, name_to_alleles_dict, species)` | Query string, `NormalizingDictionary` of member-name sequences, and `Species`; returns `(canonical_name, members, absent_genes)` or `None` | Curated haplotype/serotype definitions. Invalid members emit `UserWarning` and are omitted. Other errors propagate. |
| `Parser.parse_explicit_species_allele_candidates(name)` | String to list of transformed `Allele` candidates | Narrow path for explicit species and at least two numeric fields. Returns `[]` outside that grammar, for non-strings, or in verbose mode; caller chooses whether to fall back. Applies this Parser's alias/transform settings. |
| `Parser.parse_renamed_allele(species, source_gene, source_mhc_class, target_gene_name, target_allele_name, raw_string)` | `Species`, optional source `Gene`/class, optional target gene name, target allele string, optional raw input; returns `Allele`, `AlleleWithoutGene`, or `None` | Constructs a rename target, preserving source class for geneless targets. Unknown genes or unparseable targets return `None`. This does not apply or transfer mutations. See the full parameter docstring. |

## Registry identities

The public identity model, lookup/index APIs, and `Parser.parse_registry_allele`
are documented with their coverage and error contracts in
[Registry accession identities](registry-identities.md).

## Species naming and curation

The following functions live in `mhcgnomes.species`. Scientific names and
prefixes are strings unless noted. They perform no network lookup and do not
turn a mechanically derived prefix into evidence of published usage.

| Function | Result and scope |
|---|---|
| `make_long_prefix(latin_name)` | Generated 4+4 string from the first two valid scientific-name words, or `None`. This is the library's compatibility shorthand, not the official 2+2 nomenclature rule; it does not check collisions. |
| `binomial_long_prefix(latin_name)` | Same shorthand only for a binomial; returns `None` for a trinomial, group, or unsuitable name. It does not check uniqueness. |
| `generated_long_prefix_count(prefix)` | Number of modeled binomials claiming the exact case-sensitive 4+4 string; zero if unknown. Does not mutate the ontology. |
| `auto_generated_prefixes_for_latin_name(latin_name)` | New ordered list: concatenated binomial first, then a 4+4 shorthand only if unique in the bundled ontology. Non-binomials return an empty list. Unknown binomials can still produce a full-name string. |
| `derive_prefix_provenance(prefix, latin_name)` | `"generated"`, `"group label"`, or `None`, using only derivation and bundled ontology. Never asserts `"designated"`; that requires source evidence. |
| `containing_species(species_objects)` | Unique claimant containing all others by ancestry, or `None`. Accepts a collection of distinct `Species`; empty or unrelated collections return `None`. |
| `hyphens_as_spaces(identifier)` | New string with hyphens replaced by spaces only when the string already has both; otherwise `None`, including non-string input. Used for lookup spelling variants. |
| `blocked_registry_prefixes()` | New set of normalized prefix keys whose bundled curation status is `blocked` or `registry_only`. Takes no arguments and does not change that registry. |

`mhcgnomes.allele.single_field_allele_names()` returns a cached read-only
mapping from `(scientific species name, canonical gene name)` to a frozenset
of historical complete one-field name strings. It supports the naming
classifier; it is not a current registry-membership API. Unknown species/genes
in the source table are omitted.

## Verified download transport

`mhcgnomes.external_data.download_to_cache(url, source, cache_path, retries=3)`
is the low-level verified transport. `source` is a `Source` carrying the expected
SHA-256; `cache_path` is a `pathlib.Path`. The function creates parent directories,
downloads to a temporary file, checks its digest, then atomically replaces the
destination. It returns `None`. It retries transient HTTP/network failures up to
the total attempt count and removes temporary files on failure. Checksum failures
and terminal transfer failures raise `ExternalDataError`; other local filesystem
errors can propagate as `OSError`. Use `resolve_source` for normal cache, mirror,
and offline resolution.

The separate source-generation API and its precedence rules are documented in
[External data](https://github.com/pirl-unc/mhcgnomes/blob/main/EXTERNAL_DATA.md).
