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

    test_indi_table4: list = [
        ["@I1@", "Mr. Fakename", "M", "1 JAN 1940", "N/A", [], ["@F1@"]],
        ["@I2@", "Mrs. Fakename", "F", "2 JAN 1941", "N/A", [], ["@F1@"]],
        ["@I3@", "Mr. Fakename III", "M", "7 JUL 2025", "N/A", ["@F1@"], []],
        ["@I4@", "Mx. Fakename III", "F", "10 JUL 2025", "N/A", ["@F1@"], []],
        ["@I5@", "Dr. Fakename", "F", "3 JAN 1940", "N/A", [], ["@F2@"]]
    ]

    test_fam_table4: list = [
        ["@F1@", "13 APR 1999", "@I1@", "@I2@", ["@I3@", "@I4@"], "N/A"],
        ["@F2@", "13 APR 1999", "@I1@", "@I5@", [], "N/A"]
    ]

    def test_smaller(self):
        self.assertRaises(Exception, marriage_after_14, (self.test_indi_table, self.test_fam_table))
        self.assertRaises(Exception, birth_before_parents_death, (self.test_indi_table2, self.test_fam_table2))
        self.assertEqual(["@I3@: Mr. Fakename III"], list_recent_births(self.test_indi_table3))
        self.assertEqual(["@F1@", "13 APR 1999", "@I1@", "@I2@", ["@I4@", "@I3@"], "N/A"],
                         order_siblings(self.test_indi_table3, self.test_fam_table3[0]))
        # Do NOT raise an exception for "N/A" birth date (by design for US31) -BS
        all_indi_fields_filled([["@I1@", "Mr. Fakename", "M", "N/A", "N/A", [], ["@F1@"]]])
        # Do NOT raise an exception for "N/A" marriage date (by design for US31/US32) -BS
        all_fam_fields_filled([["@F1@", "N/A", "@I1@", "@I2@", ["@I3@", "@I4@"], "N/A"]])
        self.assertRaises(Exception, sibling_spacing, (self.test_indi_table4, self.test_fam_table3))
        self.assertRaises(Exception, unique_families_by_spouses, (self.test_indi_table4, self.test_fam_table4))


    def test_us31_include_partial_dates(self):
        partial_indi = [
            ["@I1@", "No Birth", "M", "N/A", "N/A", [], []],
            ["@I2@", "Partial Birth", "F", "JAN 1941", "N/A", [], []],
            ["@I3@", "Partial Death", "F", "N/A", "15 APR", [], []],
            ["@I4@", "Full", "M", "1 JAN 1970", "1 JAN 2000", [], []]
        ]   

        result = include_partial_dates(partial_indi, [])
        self.assertIn("Individual @I2@ (Partial Birth) has partial birth date: JAN 1941", result)
        self.assertIn("Individual @I3@ (Partial Death) has partial death date: 15 APR", result)
        self.assertNotIn("@I4@: Full", str(result))
        
    def test_us32_reject_illegitimate_dates(self):
        illegit_indi= [
            ["@I1@", "Invalid Birth", "M", "32 JAN 1990", "N/A", [], []],
            ["@I2@", "Invalid Death", "F", "1 JAN 1990", "00 MAR 2020", [], []],
            ["@I3@", "Valid", "F", "13 DEC 1985", "N/A", [], []]
        ]

        illegit_fam = [
            ["@F1@","13 XXX 2000", "@I1@", "@I2@", [], "N/A"],
            ["@F2@", "1 JAN 2001", "@I3@","@I2@", [], "31 APR 2002"]
        ]

        result = reject_illegitimate_dates(illegit_indi, illegit_fam)
        self.assertIn("Individual @I1@ (Invalid Birth) has illegitimate birth date: 32 JAN 1990", result)
        self.assertIn("Individual @I2@ (Invalid Death) has illegitimate death date: 00 MAR 2020", result)
        self.assertIn("Family @F1@ has illegitimate marriage date: 13 XXX 2000", result)
        self.assertIn("Family @F2@ has illegitimate divorce date: 31 APR 2002", result)
        self.assertNotIn("13 DEC 1985", str(result))

if __name__ == "__main__":
    unittest.main(verbosity=2)
