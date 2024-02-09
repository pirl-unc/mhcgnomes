
import pandas as pd
from time import time
from mhcgnomes import parse

def run(n_repeats=3, filename="MHC_prot.fasta"):
    if filename.endswith("csv"):
        df = pd.read_csv(filename)
        alleles = list(df.allele.values)
    else:
        alleles = []
        with open(filename) as f:
            for l in f:
                if l.startswith(">"):
                    parts = l.split()
                    alleles.append(parts[1])
    n_alleles = len(alleles)
    print("Loaded %d alleles from %s" % (
        n_alleles,
        filename
    ))
    for i in range(n_repeats):
        t0 = time()
        parsed = [parse(a) for a in alleles]
        t = time()
        elapsed = t - t0
        assert len(parsed) == len(alleles)
        print("Iter #%d, parsed %d alleles in %0.2fs (%d alleles per second)" % (
            i + 1,
            n_alleles,
            elapsed,
            n_alleles / elapsed,
        ))

if __name__ == "__main__":
    run()
