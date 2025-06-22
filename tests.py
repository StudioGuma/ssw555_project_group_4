#!/usr/bin/env python3

import unittest
from ssw555_proj import is_valid_date_str, marriage_after_14

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

	test_indi_table: list = [
		["@I1@", "Mr. Fakename", "M", "1 JAN 2000", "N/A", [], ["@F1@"]],
		["@I2@", "Mrs. Fakename", "F", "2 JAN 1999", "N/A", [], ["@F1@"]]
	]
	test_fam_table: list = [
		["@F1@", "13 APR 2013", "@I1", "@I2", [], "N/A"]
	]

	def test_marriage_after_14(self):
		self.assertRaises(Exception, marriage_after_14(test_indi_table, test_fam_table))

if __name__ == "__main__":
	unittest.main(verbosity=2)
