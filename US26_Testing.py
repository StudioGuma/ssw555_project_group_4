import unittest
from io import StringIO
import sys
from ssw555_proj import validate_name_fields

class TestValidateNameFields(unittest.TestCase):
    def test_missing_names(self):
        indi_table = [
            ["@I1@", "John /Doe/", "M", "1 JAN 1990", "N/A", [], [], []],
            ["@I2@", "Jane", "F", "1 JAN 1985", "N/A", [], [], []],
            ["@I3@", "/Smith/", "M", "1 JAN 1970", "N/A", [], [], []],
            ["@I4@", "Mary /", "F", "1 JAN 2000", "N/A", [], [], []],
        ]

        captured_output = StringIO()
        sys.stdout = captured_output
        validate_name_fields(indi_table)
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("ERROR: US26: Individual @I2@", output)
        self.assertIn("ERROR: US26: Individual @I3@", output)
        self.assertIn("ERROR: US26: Individual @I4@", output)
        self.assertNotIn("ERROR: US26: Individual @I1@", output)

if __name__ == "__main__":
    unittest.main()
