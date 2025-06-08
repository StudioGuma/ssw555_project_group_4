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
		fam_table = PrettyTable()

		with open(argv[1], "r") as ged:
			line: string = ged.readline()

			while (line != ""):
				print("--> " + line, end="")

				params: list = line.split(" ", 2)
				for i in range(len(params)):
					params[i] = params[i].rstrip()

				# if (len(params) > 2 and (params[2] == "INDI" or params[2] == "FAM")):
				# 	print("<-- " + params[0] + " | " + params[2] + " | ", end="")
				# 	if (is_valid_tag(int(params[0]), params[2])):
				# 		print("Y", end="")
				# 	else:
				# 		print("N", end="")
				# 	print(" | " + params[1])

				# else:
				# 	print("<-- " + params[0] + " | " + params[1] + " | ", end="")
				# 	if (is_valid_tag(int(params[0]), params[1])):
				# 		print("Y", end="")
				# 	else:
				# 		print("N", end="")
					
				# 	if (len(params) > 2):
				# 		print(" | " + params[2])
				# 	else:
				# 		print("")

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
