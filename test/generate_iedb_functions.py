import pandas as pd

TEST_FILENAME = "test_iedb_names.py"
df = pd.read_csv("iedb_allele_counts.csv")

special_chars = " *:-,/."
with open(TEST_FILENAME, "w") as f:
    f.write("from mhcgnomes import parse")
    for allele_name, count in sorted(zip(
            df.allele, df["number_of_entries"])):
        fn_name = allele_name.replace("\"", "").strip()
        for c in special_chars:
            fn_name = fn_name.replace(c, "_")
        fn_name = fn_name.replace("__", "_")

        f.write(f"\ndef test_{fn_name}():")
        f.write(f"\n    # {allele_name} occurs {count} times in 2019 IEDB snapshot")
        f.write(f"\n    parse(\"{allele_name}\")")
        f.write("\n")
