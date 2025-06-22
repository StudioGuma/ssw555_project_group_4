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
		date_split: list = date.split()
		if (len(date_split) != 3 or date_split[0][0] == '0' or len(date_split[2]) != 4):
			return False

		day: int = int(date_split[0])

		month: int = Month[date_split[1]].value

		year: int = int(date_split[2])

		return is_valid_date(year, month, day)

	except Exception as e:
		print(e, file=stderr)
		return False

def cmp_dates(date1: str, date2: str) -> int:
	if (is_valid_date_str(date1) and is_valid_date_str(date2)):
		# return negative if date1 < date2, positive if date1 > date2, or 0 if date1 == date2
		date1_split: list = date1.split()
		date2_split: list = date2.split()

		day1: int = int(date1_split[0])
		month1: int = Month[date1_split[1]].value
		year1: int = int(date1_split[2])
		day2: int = int(date2_split[0])
		month2: int = Month[date2_split[1]].value
		year2: int = int(date2_split[2])

		if (year1 != year2):
			return year1 - year2
		elif (month1 != month2):
			return month1 - month2
		return day1 - day2
		
	else:
		raise Exception(argv[0] + ": comparing invalid date string")

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

					if (child_birth != "N/A"):
						if (husb_death != "N/A"):
							if (cmp_dates(child_birth, husb_death) > 0):
								raise Exception(argv[0] + ": " + child + " born after father's death")
						if (wife_death != "N/A"):
							if (cmp_dates(child_birth, wife_death) > 0):
								raise Exception(argv[0] + ": " + child + " born after mother's death")
					break

def list_recent_births(indi_table: list) -> None:
	print("Recent births")
	# Assumes valid date string

	for indi in indi_table:
		birth: str = indi[3]

		if (birth != "N/A"):
			date_split: list = birth.split()
			day: int = int(date_split[0])
			month: int = Month[date_split[1]].value
			year: int = int(date_split[2])

			birth_date = datetime(year, month, day)
			delta = datetime.now() - birth_date
			if (delta.days < 31):
				print(indi[0] + ": " + indi[1])

	print("")

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

def birth_after_marriage_and_before_divorce(indi_table: list, fam_table: list) -> None:
    for fam in fam_table:
        marr = fam[1]
        div = fam[5]

        for child in fam[4]:
            for indi in indi_table:
                if indi[0] == child and indi[3] != "N/A":
                    birth = indi[3]

                    birth_parts = birth.split()
                    if len(birth_parts) != 3 or not birth_parts[2].isdigit():
                        continue

                    if marr != "N/A" and cmp_dates(birth, marr) < 0:
                        print(f"ERROR: US08: {child} born before parents' marriage")

                    if div != "N/A" and cmp_dates(birth, div) > 0:
                        print(f"ERROR: US08: {child} born after parents' divorce")

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
		fam_table_pretty.field_names = ["ID", "Date of Marriage", "Husband", "Wife", "Children", "Date of Divorce"]

		with open(argv[1], "r") as ged:
			line: string = ged.readline()

			cur_indi_row: list = ["N/A", "N/A", "N/A", "N/A", "N/A", [], []]
			cur_fam_row: list = ["N/A", "N/A", "N/A", "N/A", [], "N/A"]

			is_birth: bool = False
			is_death: bool = False
			is_marr: bool = False
			is_div: bool = False

			while (line != ""):
				params: list = line.split(" ", 2)
				for i in range(len(params)):
					params[i] = params[i].rstrip()

				level: int = int(params[0])
				match level:
					case 0:
						# add current row to the table
						if (len(params) > 2 and is_valid_tag(level, params[2])):
							match params[2]:
								case "INDI":
									if (cur_indi_row[0] != "N/A"):
										indi_table.append(cur_indi_row)
									cur_indi_row = ["N/A", "N/A", "N/A", "N/A", "N/A", [], []]

									cur_indi_row[0] = params[1]

								case "FAM":
									if (cur_fam_row[0] != "N/A"):
										fam_table.append(cur_fam_row)
									cur_fam_row = ["N/A", "N/A", "N/A", "N/A", [], "N/A"]

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

		birth_before_death(indi_table)
		marriage_before_death(indi_table, fam_table)
		birth_before_parents_death(indi_table, fam_table)
		less_than_150_years_old(indi_table)
		birth_after_marriage_and_before_divorce(indi_table, fam_table)

		for row in indi_table:
			indi_table_pretty.add_row(row)
		for row in fam_table:
			fam_table_pretty.add_row(row)

		list_recent_births(indi_table)
		
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
