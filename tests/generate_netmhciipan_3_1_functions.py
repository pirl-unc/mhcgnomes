
TEST_FILENAME = "test_netmhciipan_3_1_alleles.py"
ALLELES_FILENAME = "netmhciipan_3_1_alleles.txt"

special_chars = " *:-,/."
with open(TEST_FILENAME, "w") as f:
    f.write("from mhcgnomes import parse, Pair")
    with open(ALLELES_FILENAME) as alleles_file:
            for line in alleles_file:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue

                parts = line.split()
                allele_name = parts[0]
                fn_name = allele_name.replace("\"", "").strip()
                for c in special_chars:
                    fn_name = fn_name.replace(c, "_")
                fn_name = fn_name.replace("__", "_")

                f.write(f"\ndef test_{fn_name}():")

                f.write(f"\n    result = parse('{allele_name}', infer_class2_pairing=True)")
                f.write(f"""\n    assert result.__class__ is Pair, \\
                    'Expected parse(\"{allele_name}\") to be Pair but got %s' % (result,)""")
                f.write("\n")
