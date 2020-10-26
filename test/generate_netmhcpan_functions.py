import pandas as pd

NETMHCPAN_3_0_DEST = "test_netmhcpan_3_0_alleles.py"
NETMHCPAN_3_0_SOURCE = "netmhcpan_3_0_alleles.txt"

NETMHCPAN_4_0_DEST = "test_netmhcpan_4_0_alleles.py"
NETMHCPAN_4_0_SOURCE = "netmhcpan_4_0_alleles.txt"

special_chars = " *:-,/."


def generate(src, dst, exclude=set()):
    alleles = set()
    with open(dst, "w") as f:
        f.write("from mhcgnomes import parse, Allele, Gene, AlleleWithoutGene\n")
        with open(src) as alleles_file:
                for line in alleles_file:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    elif not line:
                        continue

                    parts = line.split()
                    allele_name = parts[0]
                    if allele_name in exclude:
                        continue
                    if allele_name in alleles:
                        print("Skipping repeat allele: '%s'" % allele_name)
                        continue
                    alleles.add(allele_name)

                    fn_name = allele_name.replace("\"", "").strip()
                    for c in special_chars:
                        fn_name = fn_name.replace(c, "_")
                    fn_name = fn_name.replace("__", "_")

                    f.write(f"\ndef test_{fn_name}():")

                    f.write(f"\n    result = parse('{allele_name}')")
                    if ":" in allele_name:
                        f.write(
                            f"""\n    assert result.__class__ is Allele, \\
                                'Expected parse(\"{allele_name}\") to be Allele but got %s' % (result,)""")
                    else:
                        f.write(
                            f"""\n    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \\
                                'Unexpected type for parse(\"{allele_name}\"): %s' % (result,)""")
                    f.write("\n")
    print(f"Wrote {len(alleles)} from {src} tests to {dst}")
    return alleles

netmhcpan_3_0_alleles = generate(
    src=NETMHCPAN_3_0_SOURCE,
    dst=NETMHCPAN_3_0_DEST)


generate(
    src=NETMHCPAN_4_0_SOURCE,
    dst=NETMHCPAN_4_0_DEST,
    exclude=netmhcpan_3_0_alleles)


