from datetime import datetime

def parse_gedcom(filename):
    individuals = {}
    families = {}

    current_individual = None
    current_family = None
    in_birth = False
    in_death = False
    in_marriage = False
    in_divorce = False

    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split(" ", 2)
            if len(parts) < 2:
                continue
            level = parts[0]
            tag = parts[1]
            value = parts[2] if len(parts) > 2 else ""

            # Identify new individual or family block
            if len(parts) == 3 and parts[2] == "INDI":
                current_individual = parts[1]  # e.g., @I1@
                individuals[current_individual] = {}
                current_family = None
            elif len(parts) == 3 and parts[2] == "FAM":
                current_family = parts[1]  # e.g., @F1@
                families[current_family] = {}
                current_individual = None
            elif tag == "NAME" and current_individual:
                individuals[current_individual]["NAME"] = value
            elif tag == "BIRT":
                in_birth = True
            elif tag == "DEAT":
                in_death = True
            elif tag == "MARR":
                in_marriage = True
            elif tag == "DIV":
                in_divorce = True
            elif tag == "DATE":
                try:
                    date_obj = datetime.strptime(value, "%d %b %Y")
                except:
                    continue
                if in_birth and current_individual:
                    individuals[current_individual]["BIRT"] = date_obj
                    in_birth = False
                elif in_death and current_individual:
                    individuals[current_individual]["DEAT"] = date_obj
                    in_death = False
                elif in_marriage and current_family:
                    families[current_family]["MARR"] = date_obj
                    in_marriage = False
                elif in_divorce and current_family:
                    families[current_family]["DIV"] = date_obj
                    in_divorce = False
            elif tag == "HUSB" and current_family:
                families[current_family]["HUSB"] = value
            elif tag == "WIFE" and current_family:
                families[current_family]["WIFE"] = value

    return individuals, families


def birth_before_marriage(individuals, families):
    errors = []
    for fam_id, fam in families.items():
        husb = individuals.get(fam.get("HUSB"))
        wife = individuals.get(fam.get("WIFE"))
        marriage_date = fam.get("MARR")

        if marriage_date:
            if husb and "BIRT" in husb and husb["BIRT"] > marriage_date:
                errors.append(f"ERROR: FAMILY: US07: {fam_id}: Husband {husb['NAME']} born after marriage.")
            if wife and "BIRT" in wife and wife["BIRT"] > marriage_date:
                errors.append(f"ERROR: FAMILY: US07: {fam_id}: Wife {wife['NAME']} born after marriage.")
    return errors


def death_before_divorce(individuals, families):
    errors = []
    for fam_id, fam in families.items():
        divorce_date = fam.get("DIV")
        if not divorce_date:
            continue

        husb = individuals.get(fam.get("HUSB"))
        wife = individuals.get(fam.get("WIFE"))

        if husb and "DEAT" in husb and husb["DEAT"] < divorce_date:
            errors.append(f"ERROR: FAMILY: US08: {fam_id}: Husband {husb['NAME']} died before divorce.")
        if wife and "DEAT" in wife and wife["DEAT"] < divorce_date:
            errors.append(f"ERROR: FAMILY: US08: {fam_id}: Wife {wife['NAME']} died before divorce.")
    return errors


if __name__ == "__main__":
    individuals, families = parse_gedcom("ssw555_proj1.ged")

    print("Running US07 (Birth Before Marriage):")
    print("\n".join(birth_before_marriage(individuals, families)))

    print("\nRunning US08 (Death Before Divorce):")
    print("\n".join(death_before_divorce(individuals, families)))


