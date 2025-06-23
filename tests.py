#!/usr/bin/env python3

import unittest
from ssw555_proj import is_valid_date_str, list_living_married

class Tests(unittest.TestCase):
	def test_valid_date_positives(self):
		self.assertTrue(is_valid_date_str("13 JUN 2025"))
		self.assertTrue(is_valid_date_str("25 DEC 1997"))
		self.assertTrue(is_valid_date_str("1 JAN 1970"))
		self.assertTrue(is_valid_date_str("15 FEB 1870"))
		self.assertTrue(is_valid_date_str("29 FEB 2024"))

	def test_valid_date_negatives(self):
		self.assertFalse(is_valid_date_str("13 JUNE 2025"))
		self.assertFalse(is_valid_date_str("01 JAN 1970"))
		self.assertFalse(is_valid_date_str("19 8 4"))
		self.assertFalse(is_valid_date_str("3 APR 3"))
		self.assertFalse(is_valid_date_str("thisisavaliddatestringiswear"))
		self.assertFalse(is_valid_date_str(""))
		self.assertFalse(is_valid_date_str("29 FEB 2023"))
		self.assertFalse(is_valid_date_str("31 APR 2100"))

	def test_list_living_married(self):
		indi_table = [
			["@I1@", "John Doe", "M", "01 JAN 1970", "N/A", [], ["@F1@"]],
			["@I2@", "Jane Doe", "F", "01 JAN 1972", "N/A", [], ["@F1@"]],
			["@I3@", "Han Solo", "M", "01 JAN 1950", "N/A", [], ["@F2@"]],
			["@I4@", "Princess Leia", "F", "01 JAN 1980", "N/A", [], []],
		]

		fam_table=[
			["@F1@", "01 JAN 1995", "@I1@", "@I2@", [], "N/A"],
			["@F2@", "01 JAN 1990", "@I3@", "@I2@", [], "N/A"]
		]

		expected=[("@I1@", "John Doe"), ("@I2@", "Jane Doe")]
		result=list_living_married(indi_table, fam_table)
		self.assertEqual(result, expected)

	

if __name__ == "__main__":
	unittest.main(verbosity=2)
