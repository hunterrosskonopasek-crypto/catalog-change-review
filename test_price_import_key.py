import subprocess
import sys
import unittest
from pathlib import Path


class PriceKeyExampleTest(unittest.TestCase):
    def test_documented_replay(self):
        sample = Path(__file__).resolve().parent / "examples" / "price-import-key"
        result = subprocess.run([sys.executable, str(sample / "replay.py")],
                                capture_output=True, text=True, check=True)
        readme = (sample / "README.md").read_text(encoding="utf-8")
        expected = readme.split("```text\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(result.stdout.strip(), expected)


if __name__ == "__main__":
    unittest.main()
