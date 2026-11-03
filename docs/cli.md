# Command line

The `mhcgnomes` executable parses names from arguments or stdin and prints a
table, and `mhcgnomes data` manages the pinned external IMGT/IPD files. Use it
to inspect how a name parses without writing Python.

## Parsing names

```bash
mhcgnomes "HLA-A*02:01" "DQ2.5"
# or:
python -m mhcgnomes "HLA-A*02:01" "DQ2.5"
```

```
input       | type   | normalized                | compact             | species | gene      | mhc_class | properties                                                                                                                                                                                                      
------------+--------+---------------------------+---------------------+---------+-----------+-----------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
HLA-A*02:01 | Allele | HLA-A*02:01               | A0201               | HLA     | A         | Ia        | species_prefix=HLA; species_name=Homo sapiens; species_latin_name=Homo sapiens; gene=HLA-A; mhc_class=Ia; mutations=; is_mutant=False; pseudogene_status=; is_pseudogene=False; allele=HLA-A*02:01; annotations=
DQ2.5       | Pair   | HLA-DQA1*05:01/DQB1*02:01 | DQA1*0501-DQB1*0201 | HLA     | DQA1/DQB1 | IIa       | gene=DQA1/DQB1; mhc_class=IIa; is_mutant=False; allele=HLA-DQA1*05:01/DQB1*02:01                                                                                                                                
```

The columns are the input string, the parsed result type, the normalized and
compact forms, species/gene/MHC class, and the parsed properties from
`to_record()`.

With no positional arguments, non-empty lines are read from stdin.

## Machine-readable output

```bash
mhcgnomes --format tsv "HLA-A*02:01" "HLA-A2"
mhcgnomes --format json "HLA-A*02:01" "not a real allele"
```

```json
[
  {
    "input": "HLA-A*02:01",
    "type": "Allele",
    "normalized": "HLA-A*02:01",
    "compact": "A0201",
    "species": "HLA",
    "gene": "A",
    "mhc_class": "Ia",
    "properties": "species_prefix=HLA; species_name=Homo sapiens; species_latin_name=Homo sapiens; gene=HLA-A; mhc_class=Ia; mutations=; is_mutant=False; pseudogene_status=; is_pseudogene=False; allele=HLA-A*02:01; annotations="
  },
  {
    "input": "not a real allele",
    "type": "ParseError",
    "normalized": "",
    "compact": "",
    "species": "",
    "gene": "",
    "mhc_class": "",
    "properties": "Could not parse 'not a real allele'"
  }
]
```

`--no-header` omits the header row from `table` and `tsv` output.

## Unparseable input

By default, unparseable values are shown as `ParseError` rows, as above. Use
strict mode to fail fast instead; it exits with status 1 on the first parse
error:

```bash
mhcgnomes --strict "not a real allele"
```

```
ParseError: Could not parse 'not a real allele'
```

## Parsing options

`--default-species` sets the species used when the input has no prefix (`HLA`
by default), `--infer-class2-pairing` fills in the canonical class II alpha
chain when only a beta chain is given, and `--max-allele-fields` restricts
parsed alleles to that many fields. `mhcgnomes --help` lists them all.

## External data

The source inventory is available offline. It groups checksum-pinned IMGT/IPD
files by purpose and reports whether each file is verified in the destination,
verified in the shared cache, missing, or invalid.

```sh
mhcgnomes data list
mhcgnomes data list --group validation
mhcgnomes data list --destination /path/to/data --cache-dir /path/to/cache
mhcgnomes data download --group validation
mhcgnomes data validate
```

`mhcgnomes data` is an alias for `mhcgnomes data list`. See
`mhcgnomes data download --help` for retrieval options, and
[External IMGT/IPD data](https://github.com/pirl-unc/mhcgnomes/blob/main/EXTERNAL_DATA.md)
for checksums, local/CI caches, optional mirrors, offline use, and alias
regeneration. `mhcgnomes data validate` parses every allele name in the
downloaded validation FASTA files; it is the same command as
`mhcgnomes-validate-data`.
