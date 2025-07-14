import unittest
from io import StringIO
import sys
from ssw555_proj import validate_dates_before_today

class TestValidateDatesBeforeToday(unittest.TestCase):
    def test_future_dates(self):
        indi_table = [
            ["@I1@", "John /Doe/", "M", "1 JAN 2030", "N/A", [], []],  # future birth
            ["@I2@", "Jane /Smith/", "F", "1 JAN 1990", "1 JAN 2035", [], []],  # future death
        ]
        
        fam_table = [
            ["@F1@", "1 JAN 2031", "@I1@", "@I2@", [], "1 JAN 2032"],  # future marriage and divorce
        ]

        # Redirect stdout to capture print output
        captured_output = StringIO()
        sys.stdout = captured_output

        validate_dates_before_today(indi_table, fam_table)

        sys.stdout = sys.__stdout__  # Reset redirect

        output = captured_output.getvalue()

        self.assertIn("ERROR: US18: Individual @I1@ has birth date in the future.", output)
        self.assertIn("ERROR: US18: Individual @I2@ has death date in the future.", output)
        self.assertIn("ERROR: US18: Family @F1@ has marriage date in the future.", output)
        self.assertIn("ERROR: US18: Family @F1@ has divorce date in the future.", output)

if __name__ == "__main__":
    unittest.main()
