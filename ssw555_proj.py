#!/usr/bin/env python3

from sys import *
from prettytable import PrettyTable

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

	return false

def main() -> int:
	try:
		if (len(argv) != 2):
			raise Exception("Usage: " + argv[0] + " <file>")
		if (not argv[1].lower().endswith(".ged")):
			raise Exception(argv[0] + ": input file is not a GEDCOM file (.ged)")

		indi_table = PrettyTable()
		indi_table.field_names = ["ID", "Name", "Gender", "Date of Birth", "Date of Death",
		"Child in", "Spouse in"]
		fam_table = PrettyTable()
		fam_table.field_names = ["ID", "Date of Marriage", "Husband", "Wife", "Children", "Date of Divorce"]

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
										indi_table.add_row(cur_indi_row)
									cur_indi_row = ["N/A", "N/A", "N/A", "N/A", "N/A", [], []]

									cur_indi_row[0] = params[1]

								case "FAM":
									if (cur_fam_row[0] != "N/A"):
										fam_table.add_row(cur_fam_row)
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
		
		print("Individuals")
		print(indi_table)
		print("Families")
		print(fam_table)

	except Exception as e:
		print(e, file=stderr)
		return 1

	return 0

if __name__ == "__main__":
	exit(main())
