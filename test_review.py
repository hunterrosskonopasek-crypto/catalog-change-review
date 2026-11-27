import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from review import compare, main


class SnapshotTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.left = Path(tmp.name, "before.csv")
        self.right = Path(tmp.name, "after.csv")

    def files(self, a, b):
        for path, rows in ((self.left, a), (self.right, b)):
            path.write_text("sku,selling_unit,pack_qty\n" + rows, encoding="utf-8")

    def test_same_and_leading_zero(self):
        self.files("01,each,1\n1,case,2", "1,case,2\n01,each,1")
        self.assertEqual(compare(self.left, self.right)["counts"], {})

    def test_demo_snapshot(self):
        base = Path(__file__).parent / "examples"
        report = compare(base/"before.csv", base/"after.csv")
        self.assertEqual(report["counts"], {"added":1, "ambiguous_key":1, "changed":1, "removed":1})
        self.assertEqual(report["findings"][0]["changed_columns"], ["pack_qty"])
        self.assertEqual(report["findings"][1]["after_records"], [3, 4])
        self.assertNotIn("A-09", str(report))

    def test_blanks_and_embedded_newline(self):
        self.files(',"each\nunit",1\nK,each,1', 'K,each,1\n   ,each,1')
        self.assertEqual(compare(self.left, self.right)["counts"], {"missing_key":2})

    def test_multiple_changes_and_dynamic_fields(self):
        self.files("K,each,1", "K,case,5")
        self.assertEqual(compare(self.left, self.right)["findings"][0]["changed_columns"], ["selling_unit","pack_qty"])
        self.assertEqual(compare(self.left, self.right, fields=["pack_qty"])["findings"][0]["changed_columns"], ["pack_qty"])

    def test_bad_csv_is_error(self):
        self.files("K,case,6", "K,each")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([str(self.left), str(self.right)]), 2)

    def test_bad_headers_and_field_specs(self):
        self.files("K,case,6", "K,case,6")
        for fields in (["sku"], ["selling_unit","selling_unit"], ["unavailable"]):
            with self.assertRaises(ValueError):
                compare(self.left, self.right, fields=fields)
        self.left.write_text("sku,sku,pack_qty\nA,A,6", encoding="utf-8")
        with self.assertRaises(ValueError):
            compare(self.left, self.right)

    def run_gate(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(["--fail-on-change", str(self.left), str(self.right)])
        return status, json.loads(stdout.getvalue()), stderr.getvalue()

    def test_key_error_threshold_and_ordinary_changes(self):
        for count in (50, 51):
            with self.subTest(count=count):
                self.files("", ",case,6\n" * count)
                status, report, notice = self.run_gate()
                self.assertEqual(status, 1)
                self.assertEqual(report["counts"], {"missing_key": count})
                self.assertEqual("$750" in notice, count > 50)
                self.assertEqual("$149/month" in notice, count > 50)
        self.files("", "".join(f"K{i},case,6\n" for i in range(60)))
        self.assertEqual(self.run_gate()[2], "")

    def test_multi_erp_schema_notice_preserves_clean_gate_and_report(self):
        for headers, rows, expected in [
            ("sap_material_number,netsuite_internal_id", "A,0042,7", True),
            ("source_erp", "A,NetSuite\nB,SAP", True),
            ("erp_system", "A,netsuite\nB,Oracle NetSuite", False),
            ("vendor,internal_id", "A,x,42\nB,y,34", False),
        ]:
            with self.subTest(headers=headers):
                data = f"sku,selling_unit,pack_qty,{headers}\n"
                for row in rows.splitlines():
                    sku, source = row.split(",", 1)
                    data += f"{sku},each,1,{source}\n"
                for path in (self.left, self.right):
                    path.write_text(data, encoding="utf-8")
                status, report, notice = self.run_gate()
                self.assertEqual(status, 0)
                self.assertEqual(report, compare(self.left, self.right))
                self.assertEqual("multiple ERP systems" in notice, expected)
                self.assertEqual("$149/month" in notice, expected)

    def test_exit_codes(self):
        self.files("K,case,6", "K,case,8")
        args = [str(self.left), str(self.right)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(args), 0)
            self.assertEqual(main(["--fail-on-change", "--", *args]), 1)
            self.files("K,case,6", "K,case,6")
            self.assertEqual(main(["--fail-on-change", "--", *args]), 0)


if __name__ == "__main__":
    unittest.main()
