from collections import defaultdict, OrderedDict
import argparse
import sys
import xml.etree.ElementTree as ET
import yaml

import pandas as pd

parser = argparse.ArgumentParser(
    prog="combine_allele_aliases.py",
    description="Combine databases with manually curated allele aliases")

parser.add_argument("--yaml-input-file", "-y", nargs="+")
parser.add_argument("--xml-input-file", "-x", nargs="+")
parser.add_argument("--allele-history-input-file", "-a", nargs="+")
parser.add_argument("--csv-input-file", "-s", nargs="+")
parser.add_argument("--output", "-o", required=True)

def valid_name(name):
    if "(" in name or ")" in name:
        return False
    return not name.replace(":", "").isdigit()

def sufficiently_different_name(old_name, new_name):
    if old_name == new_name:
        return False
    old_name_without_seps = old_name.replace(":", "")
    new_name_without_seps = new_name.replace(":", "")
    if old_name_without_seps == new_name_without_seps:
        return False
    if old_name.count(":") > 0 and old_name_without_seps in new_name:
        return False
    return True

class MappingAccumulator(object):
    def __init__(self):
        self.species_to_old_to_new = defaultdict(OrderedDict)
        self.ambiguous_names = defaultdict(set)

    def update(self, species, old_name, new_name):
        old_name = old_name.strip()
        if not valid_name(old_name):
            return False
        if old_name in self.ambiguous_names[species]:
            return False
        new_name = new_name.strip()
        if not valid_name(new_name):
            return False
        if not sufficiently_different_name(old_name, new_name):
            return False
        if old_name in self.species_to_old_to_new[species]:
            existing_value = self.species_to_old_to_new[species][old_name]
            if new_name == existing_value or existing_value.startswith(new_name):
                return False
            elif new_name.startswith(existing_value):
                # if there's a version of the new allele with more
                # fields then keep that instead
                self.species_to_old_to_new[species][old_name] = new_name
                return True
            else:
                del self.species_to_old_to_new[species][old_name]
                self.ambiguous_names[species].add(old_name)
                return False
        else:
            self.species_to_old_to_new[species][old_name] = new_name
            return True

    def merge_dictionary(self, d):
        for species, species_dict in d.items():
            for old_name, new_name in species_dict.items():
                self.update(species, old_name, new_name)



def main(args_list):
    args = parser.parse_args(args_list)
    accum = MappingAccumulator()

    if args.xml_input_file:
        for xml_file in args.xml_input_file:
            print("Loading XML source %s" % xml_file)
            tree = ET.parse(xml_file)
            root = tree.getroot()
            entries = root.find("entries")
            for entry in entries:
                name_obj = entry.find("name")
                if name_obj is None:
                    continue
                name = name_obj.text
                if "-" not in name:
                    raise ValueError("Missing species in %s" % name)
                parts = name.split("-")
                species = parts[0]
                name_without_species = "-".join(parts[1:])
                nomenclature_obj = entry.find("nomenclature")
                if not nomenclature_obj:
                    continue
                for old_name_obj in nomenclature_obj:
                    old_names = old_name_obj.text
                    for old_name in old_names.split(","):
                        accum.update(species, old_name, name_without_species)

    if args.yaml_input_file:
        for yaml_filename in args.yaml_input_file:
            print("Loading YAML source %s" % yaml_filename)
            with open(yaml_filename) as yaml_file:
                d = yaml.safe_load(yaml_file.read())
                accum.merge_dictionary(d)

    if args.allele_history_input_file:
        for filename in args.allele_history_input_file:
            print("Loading allele history source %s" % filename)
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(",")
                    most_recent_name = parts[1]
                    if most_recent_name == "NA":
                        continue

                    old_names = [p for p in parts[2:] if p and p != "NA"]
                    different_old_names = [
                        name
                        for name in old_names
                        if name != most_recent_name
                        and valid_name(name)
                        and sufficiently_different_name(name, most_recent_name)
                    ]
                    for old_name in different_old_names:
                        if accum.update("HLA", old_name, most_recent_name):
                            print("\t%s=>%s" % (old_name, most_recent_name))

    if args.csv_input_file:
        for filename in args.csv_input_file:
            print("Loading CSV source %s" % filename)
            df = pd.read_csv(filename, comment="#")
            assert "Allele" in df.columns
            assert "Description" in df.columns
            for old_allele, desc in zip(df.Allele, df.Description):
                new_allele = None
                for sep in ["=", "renamed", "identical to", "changed to", "Renamed"]:
                    if sep in desc:
                        parts = desc.split(sep)
                        part = parts[1]
                        new_allele = part.split()[0]
                        break
                if new_allele:
                    accum.update("HLA", old_allele, new_allele)
                else:
                    print("\tSkipping %s: %s" % (old_allele, desc))
    #  sanity check to make sure no "new name" also has an "old name" entry
    changed = True
    species_to_old_to_new = accum.species_to_old_to_new
    while changed:
        print("\n")
        changed = False
        updated = species_to_old_to_new.copy()
        for (species, species_dict) in species_to_old_to_new.items():
            for old, new in species_dict.items():
                if "-" in new:
                    if new.startswith("%s-" % species):
                        new_without_species = new[len(species) + 1:]
                        print("Removing species prefix from %s = %s" % (
                            new,
                            new_without_species))
                        del updated[species][old]
                        updated[species][old] = new_without_species
                        changed = True
                elif new in species_dict:
                    newer = species_dict[new]
                    print("\t Updating %s %s => %s => %s" % (species, old, new, newer))
                    updated[species][old] = newer
                    changed = True

        species_to_old_to_new = updated

    print("Writing %d alias mappings across %d species to %s" % (
        sum([len(species_dict) for species_dict in species_to_old_to_new.values()]),
        len(species_to_old_to_new),
        args.output))
    with open(args.output, "w") as f:
        for species, species_dict in sorted(species_to_old_to_new.items()):
            f.write("%s:\n" % species)
            for old_name, new_name in sorted(species_dict.items()):
                f.write("  %s: %s\n" % (old_name, new_name))

if __name__ == "__main__":
    main(sys.argv[1:])