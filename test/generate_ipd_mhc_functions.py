import pandas as pd

TEST_FILENAME = "test_ipd_mhc_names.py"
FASTA_FILENAME = "MHC_prot.fasta"

alleles = set()
special_chars = " *:-,/."
with open(TEST_FILENAME, "w") as f:
    f.write("from mhcgnomes import parse, Allele")
    with open(FASTA_FILENAME) as fasta:
        for line in fasta:
            if line.startswith(">"):

                parts = line.split()
                allele_name = parts[1]
                if allele_name in alleles:
                    print("Skipping repeat allele: '%s'" % (allele_name,))
                    print("-- %s" % (line,))
                    continue
                alleles.add(allele_name)
                fn_name = allele_name.replace("\"", "").strip()
                for c in special_chars:
                    fn_name = fn_name.replace(c, "_")
                fn_name = fn_name.replace("__", "_")

                f.write(f"\ndef test_{fn_name}():")
                field_count = allele_name.count(":") + 1
                if field_count == 1:
                    assert "*" in allele_name
                    after_star = allele_name.split("*")[1]
                    if not after_star.isdigit():
                        field_count = 1
                    else:
                        num_digits = len(after_star)
                        if num_digits <= 3:
                            field_count = 1
                        elif num_digits <= 5:
                            field_count = 2
                        elif num_digits <= 7:
                            field_count = 3
                        else:
                            field_count = 4
                f.write(f"\n    result = parse('{allele_name}')")
                f.write(f"""\n    assert result.__class__ is Allele, \\
                    'Expected parse(\"{allele_name}\") to be Allele but got %s' % (result,)""")
                f.write(f"""\n    assert result.num_allele_fields == {field_count}, \\
                                ('Expected parse(\"{allele_name}\") to have {field_count} ' 
                                 'field(s) but got %d') % result.num_allele_fields""")

                f.write("\n")

print("Wrote %d alleles to %s" % (len(alleles), TEST_FILENAME))