#!/usr/bin/env python3

import unittest
from ssw555_proj import *

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
	test_indi_table2: list = [
		["@I1@", "Mr. Fakename", "M", "1 JAN 1940", "2 FEB 1990", [], ["@F1@"]],
		["@I2@", "Mrs. Fakename", "F", "2 JAN 1941", "2 FEB 1990", [], ["@F1@"]],
		["@I3@", "Mrs. Fakename Jr.", "F", "2 MAR 1990", "N/A", ["@F1@"], []]
	]
	test_fam_table2: list = [
		["@F1@", "13 APR 1970", "@I1@", "@I2@", ["@I3@"], "N/A"]
	]

	test_indi_table3: list = [
		["@I1@", "Mr. Fakename", "M", "1 JAN 1940", "N/A", [], ["@F1@"]],
		["@I2@", "Mrs. Fakename", "F", "2 JAN 1941", "N/A", [], ["@F1@"]],
		["@I3@", "Mr. Fakename III", "M", "7 JUL 2025", "N/A", ["@F1@"], []],
		["@I4@", "Mx. Fakename III", "F", "25 JUN 2022", "N/A", ["@F1@"], []]
	]
	test_fam_table3: list = [
		["@F1@", "13 APR 1999", "@I1@", "@I2@", ["@I3@", "@I4@"], "N/A"]
	]

	def test_smaller(self):
		self.assertRaises(Exception, marriage_after_14(self.test_indi_table, self.test_fam_table))
		self.assertRaises(Exception, birth_before_parents_death(self.test_indi_table2, self.test_fam_table2))
		self.assertEqual(["@I3@: Mr. Fakename III"], list_recent_births(self.test_indi_table3))
		self.assertEqual(["@F1@", "13 APR 1999", "@I1@", "@I2@", ["@I4@", "@I3@"], "N/A"],
		order_siblings(self.test_indi_table3, self.test_fam_table3))

if __name__ == "__main__":
	unittest.main(verbosity=2)
