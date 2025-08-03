import unittest
from io import StringIO
import sys
from ssw555_proj import show_spouse_names

class TestShowSpouseNames(unittest.TestCase):
    def test_spouse_names_display(self):
        indi_table = [
             ["@I1@", "John /Doe/", "M", "1 JAN 1980", "N/A", [], [], []],
             ["@I2@", "Jane /Smith/", "F", "2 FEB 1985", "N/A", [], [], []],
             ["@I3@", "Mike /Brown/", "M", "3 MAR 1990", "N/A", [], [], []]
        ]
        
        fam_table = [
            ["@F1@", "@I1@", "@I2@", "1 JAN 2005", []],
            ["@F2@", "@I3@", "@I99@", "1 JAN 2010", []]
        ]

        captured_output = StringIO()
        sys.stdout = captured_output

        show_spouse_names(fam_table, indi_table)

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()

        self.assertIn("@F1@", output)
        self.assertIn("John /Doe/", output)
        self.assertIn("Jane /Smith/", output)
        self.assertIn("@F2@", output)
        self.assertIn("Unknown", output)

if __name__ == "__main__":
    unittest.main()
