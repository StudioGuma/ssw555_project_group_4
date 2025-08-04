#!/usr/bin/env python3

from sys import *
from enum import Enum
from prettytable import PrettyTable
from datetime import datetime, date

class Month(Enum):
	JAN = 1
	FEB = 2
	MAR = 3
	APR = 4
	MAY = 5
	JUN = 6
	JUL = 7
	AUG = 8
	SEP = 9
	OCT = 10
	NOV = 11
	DEC = 12

def parse_date(date_str):
	try:
		return datetime.strptime(date_str, "%d %b %Y")
	except:
		return None

def split_date(date_str: str) -> list:
	date_split: list = date_str.split()
	if (len(date_split) != 3 or date_split[0][0] == '0' or len(date_split[2]) != 4):
		raise Exception(argv[0] + ": invalid date string")

	day: int = int(date_split[0])
	month: int = Month[date_split[1]].value
	year: int = int(date_split[2])

	return [year, month, day]

def is_valid_tag(level: int, tag: str) -> bool:
	match level:
		case 0:
			return (tag == "INDI" or tag == "FAM" or tag == "HEAD" or tag == "TRLR" or tag == "NOTE")
		case 1:
			return (tag == "NAME" or tag == "SEX" or tag == "BIRT" or tag == "DEAT" or tag == "FAMC"
			or tag == "FAMS" or tag == "MARR" or tag == "HUSB" or tag == "WIFE" or tag == "CHIL"
			or tag == "DIV")
		case 2:
			return (tag == "DATE")

	return False

def is_leap_year(year: int) -> bool:
	return (year % 400 == 0) or (year % 4 == 0 and year % 100 > 0)

def is_valid_date(year: int, month: int, day: int) -> bool:
	if (day > 0):
		match month:
			case 1 | 3 | 5 | 7 | 8 | 10 | 12:
				return (day <= 31)

			case 2:
				return (day <= 29 if is_leap_year(year) else day <= 28)

			case 4 | 6 | 9 | 11:
				return (day <= 30)

	return False

def is_valid_date_str(date: str) -> bool:
	try:
		date_split: list = split_date(date)
		return is_valid_date(date_split[0], date_split[1], date_split[2])

	except Exception as e:
		return False

def birth_before_death(indi_table: list) -> None:
	for row in indi_table:
		id_, name, _, birth, death, _, _ = row
		birth_date = parse_date(birth)
		death_date = parse_date(death)
		if birth_date and death_date and birth_date > death_date:
			print(f"ERROR: US01: {name} ({id_}) born after death.")

def marriage_before_death(indi_table: list, fam_table: list) -> None:
	id_to_death = {row[0]: row[4] for row in indi_table}
	id_to_name = {row[0]: row[1] for row in indi_table}

	for row in fam_table:
		fam_id, marriage, husb, wife, _, _ = row
		marriage_date = parse_date(marriage)
		husb_death = parse_date(id_to_death.get(husb))
		wife_death = parse_date(id_to_death.get(wife))

		if marriage_date and husb_death and marriage_date > husb_death:
			print(f"ERROR: US02: Family {fam_id}: Marriage occurs after death of husband {id_to_name.get(husb)} ({husb})")
		if marriage_date and wife_death and marriage_date > wife_death:
			print(f"ERROR: US02: Family {fam_id}: Marriage occurs after death of wife {id_to_name.get(wife)} ({wife})")

def birth_before_parents_death(indi_table: list, fam_table: list) -> None:
	# assumes that indi_table and fam_table are properly formatted
	for fam in fam_table:
		for indi in indi_table:
			if (indi[0] == fam[2]):
				husb_death: str = indi[4]
			if (indi[0] == fam[3]):
				wife_death: str = indi[4]
			# husb_death and wife_death could still be "N/A"


		for child in fam[4]:
			for indi in indi_table:
				if (indi[0] == child):
					child_birth: str = indi[3]

					child_birth_date = parse_date(child_birth)
					if (child_birth_date):
						husb_death_date = parse_date(husb_death)
						if (husb_death_date and child_birth_date > husb_death_date):
							raise Exception(argv[0] + ": " + child + " born after parent 1's death")
						wife_death_date = parse_date(wife_death)
						if (wife_death_date and child_birth_date > wife_death_date):
							raise Exception(argv[0] + ": " + child + " born after parent 2's death")
					break

def list_recent_births(indi_table: list) -> list:
	# Assumes valid date string
	birth_list: list = []

	for indi in indi_table:
		birth: str = indi[3]

		if (birth != "N/A"):
			birth_date = parse_date(birth)
			delta = datetime.now() - birth_date
			if (delta.days < 31):
				birth_list.append(indi[0] + ": " + indi[1])

	return birth_list

def less_than_150_years_old(indi_table: list) -> None:
	for indi in indi_table:
		birth = indi[3] 
		death = indi[4]

		if birth == "N/A":
			continue
			
		birth_parts = birth.split()
		if len(birth_parts) != 3 or not birth_parts[2].isdigit():
			continue

		birth_year = int(birth_parts[2])

		if death != "N/A":
			death_parts = death.split()
			if len(death_parts) != 3 or not death_parts[2].isdigit():
				continue
			death_year = int(death_parts[2])

			if (death_year - birth_year) > 150:
				print("US07: ERROR –", indi[0], "lived more than 150 years")


#US09: No Marriages to Descendants
def no_marriage_to_descendants(fam_table: list, indi_table: list) -> None:
    parent_to_children = {}
    for fam in fam_table:
        husb, wife, children = fam[2], fam[3], fam[4]
        for parent in [husb, wife]:
            if parent not in parent_to_children:
                parent_to_children[parent] = []
            parent_to_children[parent].extend(children)

    def get_descendants(person_id, visited=None):
        if visited is None:
            visited = set()
        descendants = set()
        children = parent_to_children.get(person_id, [])
        for child in children:
            if child not in visited:
                visited.add(child)
                descendants.add(child)
                descendants.update(get_descendants(child, visited))
        return descendants

    for fam in fam_table:
        husb, wife, fam_id = fam[2], fam[3], fam[0]
        if wife in get_descendants(husb):
            print(f"ERROR: US09: Family {fam_id}: Husband {husb} is married to descendant {wife}")
        if husb in get_descendants(wife):
            print(f"ERROR: US09: Family {fam_id}: Wife {wife} is married to descendant {husb}")


#US10: No Sibling Marriages
def no_sibling_marriages(fam_table: list) -> None:
    child_to_fam = {}
    for fam in fam_table:
        for child in fam[4]:
            child_to_fam[child] = fam[0]

    for fam in fam_table:
        husb, wife, fam_id = fam[2], fam[3], fam[0]
        if husb in child_to_fam and wife in child_to_fam:
            if child_to_fam[husb] == child_to_fam[wife]:
                print(f"ERROR: US10: Family {fam_id}: Siblings {husb} and {wife} are married.")

def birth_after_marriage_and_before_divorce(indi_table: list, fam_table: list) -> None:
	for fam in fam_table:
		marr = fam[1]
		div = fam[5]

		for child in fam[4]:
			for indi in indi_table:
				if indi[0] == child and indi[3] != "N/A":
					birth = indi[3]
					birth_date = parse_date(birth)
					if (not birth_date):
						continue

					marr_date = parse_date(marr)
					div_date = parse_date(div)
					if (marr_date and birth_date < marr_date):
						print(f"ERROR: US08: {child} born before parents' marriage")

					if (div_date and birth_date > div_date):
						print(f"ERROR: US08: {child} born after parents' divorce")

def get_age_at_date(birth: str, date: str) -> int:
	b_day, b_month, b_year = birth.split()
	d_day, d_month, d_year = date.split()

	b_day, b_month, b_year = int(b_day), Month[b_month].value, int(b_year)
	d_day, d_month, d_year = int(d_day), Month[d_month].value, int(d_year)

	age = d_year - b_year



	if (b_month > d_month) or (d_month == b_month and b_day > d_day):
		age -= 1
	
	return age

def marriage_after_14(indi_table: list, fam_table: list) -> None:
	for fam in fam_table:
		marr_date: str = fam[1]
		if (marr_date != "N/A"):
			husb: str = fam[2]
			wife: str = fam[3]

			husb_birth: str = "N/A"
			wife_birth: str = "N/A"

			for indi in indi_table:
				if (husb != "N/A" and indi[0] == husb):
					husb_birth: str = indi[3]

				if (wife != "N/A" and indi[0] == wife):
					wife_birth: str = indi[3]
			

			if (husb_birth != "N/A"):
				age = get_age_at_date(husb_birth, marr_date)

				if (age < 14):
					print(f"ERROR: In family {fam[0]}: Husband {husb} was married before the age of 14.")
			
			if (wife_birth != "N/A"):
				age = get_age_at_date(wife_birth, marr_date)

				if (age < 14):
					print(f"ERROR: In family {fam[0]}: Wife {wife} was married before the age of 14.")

def list_living_married(indi_table: list, fam_table: list) -> list:
    living_married = []
    married_set = set()

    for fam in fam_table:
        husb_id = fam[2]
        wife_id = fam[3]
        marriage_date = fam[1]
        divorce_date = fam[5]

        if husb_id and wife_id and marriage_date != "N/A" and divorce_date == "N/A":
            married_set.add(husb_id)
            married_set.add(wife_id)

    for indi in indi_table:
        if indi[0] in married_set and indi[4] == "N/A":
            living_married.append((indi[0], indi[1]))

    if living_married:
        print("\nLiving Married Individuals:")
        for indi_id, name in living_married:
            print(f"{indi_id}: {name}")

    return living_married

def list_orphans(indi_table: list, fam_table: list) -> list:
    orphans = []
    id_to_parents = {indi[0]: [] for indi in indi_table}
    id_to_birth = {indi[0]: indi[3] for indi in indi_table}
    id_to_death = {indi[0]: indi[4] for indi in indi_table}

    for fam in fam_table:
        for child_id in fam[4]:  
            if fam[2] != "N/A":
                id_to_parents[child_id].append(fam[2])  
            if fam[3] != "N/A":
                id_to_parents[child_id].append(fam[3])  

    for indi in indi_table:
        indi_id, name, gender, birth, death, famc, _ = indi
        if death != "N/A":
            continue 

        birth_parts = birth.split()
        if len(birth_parts) != 3 or not birth_parts[2].isdigit():
            continue

        birth_year = int(birth_parts[2])
        if birth_year >= datetime.now().year - 18:
            parents = id_to_parents.get(indi_id, [])
            if all(id_to_death.get(pid, "N/A") != "N/A" for pid in parents):
                orphans.append((indi_id, name))

    if orphans:
        print("\nOrphans (US16):")
        for oid, name in orphans:
            print(f"{oid}: {name}")
    return orphans

def is_sorted(lst: list) -> bool:
	for i in range(len(lst) - 1):
		if (lst[i] > lst[i + 1]):
			return False

	return True

def order_siblings(indi_table: list, fam: list) -> list:
	sibling_list: list = fam[4]
	birth_list: list = []

	for sibling in sibling_list:
		for indi in indi_table:
			if (indi[0] == sibling):
				birth_list.append(indi[3])

	bd_list: list = list(map(parse_date, birth_list))

	while (not is_sorted(bd_list)):
		for i in range(len(bd_list) - 1):
			if (bd_list[i] > bd_list[i + 1]):
				bd_list[i], bd_list[i + 1] = bd_list[i + 1], bd_list[i]
				sibling_list[i], sibling_list[i + 1] = sibling_list[i + 1], sibling_list[i]

	fam[4] = sibling_list
	return fam

def all_indi_fields_filled(indi_table: list) -> None:
	for indi in indi_table:
		if (indi[0] == "N/A"):
			raise Exception(argv[0] + ": individual ID must be filled")
		if (indi[1] == "N/A"):
			raise Exception(argv[0] + f": name of individual {indi[0]} must be filled")
		if (not is_valid_date_str(indi[3])):
			raise Exception(argv[0] + f": birth date of individual {indi[0]} must be valid")
	return

def all_fam_fields_filled(fam_table: list) -> None:
	for fam in fam_table:
		if (fam[0] == "N/A"):
			raise Exception(argv[0] + f": family ID must be filled")
		if (not is_valid_date_str(fam[1])):
			raise Exception(argv[0] + f": marriage date of family {fam[0]} must be filled")
		if (fam[2] == "N/A"):
			raise Exception(argv[0] + f": parent 1 of family {fam[0]} must be filled")
		if (fam[3] == "N/A"):
			raise Exception(argv[0] + f": parent 2 of family {fam[0]} must be filled")
	return
		

def list_families_sorted_by_marriage(fam_table: list) -> None:
    valid_fams = [fam for fam in fam_table if fam[1] != "N/A"]
    
    valid_fams.sort(key=lambda fam: datetime.strptime(fam[1], "%d %b %Y"))

    for fam in valid_fams:
        fam_id = fam[0]
        husb_id = fam[2]
        wife_id = fam[3]
        marr_date = fam[1]
        print(f"Family {fam_id}: Husband {husb_id}, Wife {wife_id} | Married: {marr_date}")

def validate_dates_before_today(indi_table: list, fam_table: list) -> None:
    today = datetime.today()

    def is_future_date(date_str: str) -> bool:
        parsed = parse_date(date_str)
        return parsed and parsed > today

    for indi in indi_table:
        if is_future_date(indi[3]):
            print(f"ERROR: US18: Individual {indi[0]} has birth date in the future.")
        if is_future_date(indi[4]):
            print(f"ERROR: US18: Individual {indi[0]} has death date in the future.")

    for fam in fam_table:
        if is_future_date(fam[1]):
            print(f"ERROR: US18: Family {fam[0]} has marriage date in the future.")
        if is_future_date(fam[5]):
            print(f"ERROR: US18: Family {fam[0]} has divorce date in the future.")

def show_divorce_dates(fam_table: list, indi_table: list) -> None:
    id_to_name = {}

    for indi in indi_table:
        indi_id = indi[0]
        indi_name = indi[1]
        id_to_name[indi_id] = indi_name

    print("Divorce Dates:")

    for fam in fam_table:
        fam_id = fam[0]
        divorce_date = fam[5]

        if divorce_date != "N/A":

            husb_id = fam[2]
            wife_id = fam[3]

            husb_name = id_to_name.get(husb_id, "Unknown")
            wife_name = id_to_name.get(wife_id, "Unknown")

            print(f"Family {fam_id}: {husb_name} and {wife_name} divorced on {divorce_date}")

def display_marriages_per_person(fam_table: list, indi_table: list) -> None:
    id_to_name = {}
    marriages = {}

    for indi in indi_table:
        indi_id = indi[0]
        indi_name = indi[1]
        id_to_name[indi_id] = indi_name
        marriages[indi_id] = []
    for fam in fam_table:
        marriage_date = fam[1]
        husb = fam[2]
        wife = fam[3]
        if marriage_date != "N/A":
            if husb in marriages:
                marriages[husb].append((wife, marriage_date))
            else:
                marriages[husb] = [(wife, marriage_date)]
            if wife in marriages:
                marriages[wife].append((husb, marriage_date))
            else:
                marriages[wife] = [(husb, marriage_date)]
    print("Marriages Per Person:")

    for person_id in marriages:
        spouse_data = marriages[person_id]

        if not spouse_data:
            continue
        for spouse_id, date in spouse_data:
            person_name = id_to_name.get(person_id, "Unknown")
            spouse_name = id_to_name.get(spouse_id, "Unknown")
            print(f"{person_name} ({person_id}) married {spouse_name} ({spouse_id}) on {date}")

def sibling_spacing(indi_table: list, fam_table: list) -> None:
	for fam in fam_table:
		siblings = fam[4]
		sibling_births: list = []

		for sibling in siblings:
			for indi in indi_table:
				if indi[0] == sibling:
					sibling_births.append(indi[3])
					break

		sibling_bds: list = list(map(parse_date, sibling_births))
		for i in range(len(sibling_bds)):
			for j in range(i + 1, len(sibling_bds)):
				days: int = abs((sibling_bds[i] - sibling_bds[j]).days)
				if (2 < days < 210):
					raise Exception(f"{argv[0]}: \
					siblings were born more than 2 days but less than 9 months apart")


def unique_families_by_spouses(indi_table: list, fam_table: list) -> None:
	# create a list of lists of each family's spouse names and marriage date
	fam_info: list = []

	for fam in fam_table:
		new_elem: list = []
		new_elem.append(fam[1])

		for indi in indi_table:
			if (indi[0] == fam[2] or indi[0] == fam[3]):
				new_elem.append(indi[1])

		new_elem.sort()
		fam_info.append(new_elem)

	print(fam_info)

	fam_no_dups: list = []
	for fam in fam_info:
		if fam not in fam_no_dups:
			fam_no_dups.append(fam)

	if (len(fam_info) != len(fam_no_dups)):
		raise Exception(f"{argv[0]}: multiple families have the same spouses and marriage date")

def main() -> int:
	try:
		if (len(argv) != 2):
			raise Exception("Usage: " + argv[0] + " <file>")
		if (not argv[1].lower().endswith(".ged")):
			raise Exception(argv[0] + ": input file is not a GEDCOM file (.ged)")

		indi_table: list = []
		indi_table_pretty = PrettyTable()
		indi_table_pretty.field_names = ["ID", "Name", "Gender", "Date of Birth", "Date of Death",
		"Child in", "Spouse in"]
		fam_table: list = []
		fam_table_pretty = PrettyTable()
		fam_table_pretty.field_names = ["ID", "Date of Marriage", "Parent 1", "Parent 2", "Children", "Date of Divorce"]

		with open(argv[1], "r") as ged:
			line: string = ged.readline()

			cur_indi_row: list = ["N/A", "N/A", "N/A", "N/A", "N/A", [], []]
			cur_fam_row: list = ["N/A", "N/A", "N/A", "N/A", [], "N/A"]

			is_birth: bool = False
			is_death: bool = False
			is_marr: bool = False
			is_div: bool = False

			while (line != ""):
				line = line.strip('\n')
				params: list = line.split(" ", 2)
				for i in range(len(params)):
					params[i] = params[i].rstrip()

				level: int = int(params[0])
				match level:
					case 0:
						# add current row to the table
						if (len(params) > 2 and is_valid_tag(level, params[2])
						or len(params) > 1 and params[1] == "TRLR"):
							if (cur_indi_row[0] != "N/A"):
								indi_table.append(cur_indi_row)
							cur_indi_row = ["N/A", "N/A", "N/A", "N/A", "N/A", [], []]
							if (cur_fam_row[0] != "N/A"):
								fam_table.append(cur_fam_row)
							cur_fam_row = ["N/A", "N/A", "N/A", "N/A", [], "N/A"]

							if (len(params) > 2):
								match params[2]:
									case "INDI":
										cur_indi_row[0] = params[1]

									case "FAM":
										cur_fam_row[0] = params[1]

					case 1:
						if (is_valid_tag(level, params[1])):
							match params[1]:
								case "NAME":
									cur_indi_row[1] = params[2]

								case "SEX":
									cur_indi_row[2] = params[2]

								case "BIRT":
									is_birth = True

								case "DEAT":
									is_death = True

								case "FAMC":
									cur_indi_row[5].append(params[2])

								case "FAMS":
									cur_indi_row[6].append(params[2])

								case "MARR":
									is_marr = True

								case "HUSB":
									cur_fam_row[2] = params[2]

								case "WIFE":
									cur_fam_row[3] = params[2]

								case "CHIL":
									cur_fam_row[4].append(params[2])

								case "DIV":
									is_div = True

					case 2:
						if (len(params) > 2 and is_valid_tag(level, params[1])):
							# guaranteed to be DATE
							if (not is_valid_date_str(params[2])):
								raise Exception(argv[0] + ": invalid date " + line)

							if is_birth:
								cur_indi_row[3] = params[2]
								is_birth = False

							elif is_death:
								cur_indi_row[4] = params[2]
								is_death = False

							elif is_marr:
								cur_fam_row[1] = params[2]
								is_marr = False

							elif is_div:
								cur_fam_row[5] = params[2]
								is_div = False

				line = ged.readline()

		all_indi_fields_filled(indi_table)
		all_fam_fields_filled(fam_table)

		birth_before_death(indi_table)
		marriage_before_death(indi_table, fam_table)
		birth_before_parents_death(indi_table, fam_table)
		less_than_150_years_old(indi_table)
		birth_after_marriage_and_before_divorce(indi_table, fam_table)
		marriage_after_14(indi_table, fam_table)
		no_marriage_to_descendants(fam_table, indi_table)
		no_sibling_marriages(fam_table)
		list_living_married(indi_table, fam_table)
		list_orphans(indi_table, fam_table)
		validate_dates_before_today(indi_table, fam_table)
		list_families_sorted_by_marriage(fam_table)
		show_divorce_dates(fam_table, indi_table)
		display_marriages_per_person(fam_table, indi_table)
		unique_families_by_spouses(indi_table, fam_table)

		for fam in fam_table:
			fam = order_siblings(indi_table, fam)

		for row in indi_table:
			indi_table_pretty.add_row(row)
		for row in fam_table:
			fam_table_pretty.add_row(row)

		print("Recent births")
		print(*list_recent_births(indi_table), sep='\n')
		
		print("Individuals")
		print(indi_table_pretty)
		print("Families")
		print(fam_table_pretty)

	except Exception as e:
		print(e, file=stderr)
		return 1

	return 0

if __name__ == "__main__":
	exit(main())
