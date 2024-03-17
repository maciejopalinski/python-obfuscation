#!/usr/bin/env python3

import unittest
import subprocess
import obf, deobf

class TestSimple(unittest.TestCase):
    def test(self):
        source_code = "for i in range(100): print(i)"
        obfuscated_code = obf.iteration(source_code, 1, False, None, 300)
        deobfuscated_code = deobf.iteration(obfuscated_code, 1, False, None, None)

        self.assertEqual(source_code, deobfuscated_code, "code is not equal")

        source_result = subprocess.run(["/usr/bin/env", "python3"], capture_output=True, text=True, input=source_code)
        obfuscated_result = subprocess.run(["/usr/bin/env", "python3"], capture_output=True, text=True, input=obfuscated_code)

        self.assertEqual(source_result.stdout, obfuscated_result.stdout, "code does not have the same effect when executed")

if __name__ == "__main__":
    unittest.main()