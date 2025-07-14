import unittest
from ssw555_proj import list_families_sorted_by_marriage

class TestListFamilies(unittest.TestCase):
    def test_list_families(self):
        fam_table = [
            ["@F1@", "N/A", "@I1@", "@I2@", [], "N/A"],
            ["@F2@", "1 JAN 1980", "@I3@", "@I4@", [], "N/A"],
            ["@F3@", "5 MAY 1975", "@I5@", "@I6@", [], "N/A"],
            ["@F4@", "N/A", "@I7@", "@I8@", [], "N/A"],
            ["@F5@", "10 OCT 1990", "@I9@", "@I10@", [], "N/A"],
        ]

        print("\n--- Listing Families ---")
        list_families_sorted_by_marriage(fam_table)

if __name__ == "__main__":
    unittest.main()
