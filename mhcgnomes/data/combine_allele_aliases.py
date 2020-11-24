from collections import defaultdict, OrderedDict
import argparse
import sys
import xml.etree.ElementTree as ET
import yaml

parser = argparse.ArgumentParser(
    prog="combine_allele_aliases.py",
    description="Combine databases with manually curated allele aliases")

parser.add_argument("--yaml-input-file", "-y", nargs="+")
parser.add_argument("--xml-input-file", "-x", nargs="+")
parser.add_argument("--allele-history-input-file", "-a", nargs="+")
parser.add_argument("--deleted-alleles-input-file", "-d", nargs="+")
parser.add_argument("--output", "-o", required=True)


def main(args_list):
    args = parser.parse_args(args_list)
    species_to_old_to_new = defaultdict(OrderedDict)
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
                name_without_seps = name.replace(":", "")

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
                        old_name = old_name.strip()
                        if "(" in old_name:
                            continue
                        if old_name == name_without_species:
                            continue
                        old_name_without_seps = old_name.replace(":", "")
                        if old_name_without_seps == name_without_seps:
                            continue
                        if old_name.count(":") > 0 and old_name_without_seps in name_without_seps:
                            continue
                        species_to_old_to_new[species][old_name] = name_without_species
    if args.yaml_input_file:
        for yaml_filename in args.yaml_input_file:
            print("Loading YAML source %s" % yaml_filename)
            with open(yaml_filename) as yaml_file:
                d = yaml.safe_load(yaml_file.read())
                for species, species_dict in d.items():
                    for old_name, new_name in species_dict.items():
                        if old_name in species_to_old_to_new[species]:
                            existing_value = species_to_old_to_new[species][old_name]
                            if new_name == existing_value or existing_value.startswith(new_name):
                                continue
                            elif new_name.startswith(existing_value):
                                # if there's a version of the new allele with more
                                # fields then keep that instead
                                species_to_old_to_new[species][old_name] = new_name
                            else:
                                raise ValueError(
                                    "Found %s => %s in %s but contradicts existing value %s" % (
                                        old_name, new_name, yaml_filename, existing_value))
                        else:
                            species_to_old_to_new[species][old_name] = new_name

    #  sanity check to make sure no "new name" also has an "old name" entry
    changed = True
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