import csv
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

EXAMPLE = Path(__file__).parent / "examples" / "znode-bundle-associations"


def run(*args):
    return subprocess.run([sys.executable, str(EXAMPLE / "preflight.py"), *map(str, args)],
                          capture_output=True, text=True)


@contextmanager
def unit_inputs(bill_header="", proposal_header="", bill_values=(), proposal_values=()):
    with TemporaryDirectory() as temp:
        bill = Path(temp) / "bill.csv"
        proposal = Path(temp) / "proposal.csv"
        for path, base_header, extra_header, base_row, values in (
            (bill, "ParentSku,ChildSKU,ApprovedQuantity", bill_header, ["KIT-710", "GSK-004", "2"], bill_values),
            (proposal, "ParentSku,ChildSKU,DisplayOrder,IsDefault,Quantity", proposal_header,
             ["KIT-710", "GSK-004", "1", "0", "2"], proposal_values),
        ):
            headers = base_header.split(",") + (extra_header.split(",") if extra_header else [])
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(headers)
                writer.writerow(base_row + list(values))
        yield bill, proposal


class BundleReviewTests(unittest.TestCase):
    def test_public_worksheet_is_reproducible(self):
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, (EXAMPLE / "expected-review.csv").read_text())
        rows = list(csv.DictReader(StringIO(result.stdout)))
        self.assertEqual([r["record"] for r in rows if r["decision"] == "MATCH"], ["1", "3"])
        self.assertEqual(rows[2]["ChildSKU"], "00017")
        self.assertNotIn("proposed_uom", rows[0])
        self.assertIn("Unit basis unverified", rows[0]["reason"])

    def test_equal_quantities_require_compatible_units(self):
        for approved, proposed, decision, reason in (
            ("CASE12", "EA", "REVIEW", "units differ"),
            ("mW", "MW", "REVIEW", "units differ"),
            ("EA", "ea", "REVIEW", "units differ"),
            (" EA ", "EA", "MATCH", "including component unit"),
            (" ", "EA", "REVIEW", "unit missing"),
            ("", "", "REVIEW", "unit missing"),
        ):
            with self.subTest(approved=approved, proposed=proposed), unit_inputs(
                    "Approved UOM", "PROPOSED_UOM", [approved], [proposed]) as (bill, proposal):
                result = run("--bom", bill, "--proposed", proposal)
                self.assertEqual(result.returncode, 0, result.stderr)
                reader = csv.DictReader(StringIO(result.stdout))
                self.assertEqual(reader.fieldnames[-2:], ["proposed_uom", "approved_uom"])
                row = next(reader)
                self.assertEqual((row["approved_uom"], row["proposed_uom"]), (approved, proposed))
                self.assertEqual(row["decision"], decision)
                self.assertIn(reason, row["reason"])

    def test_compare_aliases_and_one_sided_units(self):
        for bill_col, prop_col in (
            ("unit", "units"), ("Unit of Measure", "Component_UOM"), ("Quantity Unit", "UOM"),
            ("approved_unit", "proposed unit of measure"), ("ApprovedUnitOfMeasure", "ProposedUnit"),
            ("", "UOM"), ("UOM", ""),
        ):
            with self.subTest(bill_col=bill_col, prop_col=prop_col), unit_inputs(
                    bill_col, prop_col, ["EA"] if bill_col else [], ["EA"] if prop_col else []) as (bill, proposal):
                result = run("--bom", bill, "--proposed", proposal)
                self.assertEqual(result.returncode, 0, result.stderr)
                row = next(csv.DictReader(StringIO(result.stdout)))
                self.assertEqual(row["decision"], "MATCH" if bill_col and prop_col else "REVIEW")
                self.assertEqual(row["approved_uom"], "EA" if bill_col else "")
                self.assertEqual(row["proposed_uom"], "EA" if prop_col else "")

    def test_competing_unit_columns_require_selection(self):
        for bill_col, prop_col in (("UOM,ApprovedUnit", "UOM"), ("UOM", "unit,PROPOSED_UOM")):
            with self.subTest(bill_col=bill_col), unit_inputs(
                    bill_col, prop_col, ["EA"] * len(bill_col.split(",")),
                    ["EA"] * len(prop_col.split(","))) as (bill, proposal):
                result = run("--bom", bill, "--proposed", proposal)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Select one unit column", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_exact_quantity_and_reference_coverage(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "proposal.csv"
            path.write_text("ParentSku,ChildSKU,DisplayOrder,IsDefault,Quantity\n"
                            "KIT-710,GSK-004,2,0,4.0\n"
                            "UNKNOWN,GSK-004,1,0,\n"
                            "KIT-710,=BAD,1,0,1_0\n", encoding="utf-8")
            result = run("--proposed", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            corrected, unknown, malformed = csv.DictReader(StringIO(result.stdout))
            self.assertEqual(corrected["decision"], "MATCH")
            self.assertIn("Parent SKU absent", unknown["reason"])
            self.assertNotIn("Missing bundle component quantity", unknown["reason"])
            self.assertEqual(malformed["ChildSKU"], "'=BAD")
            self.assertIn("Review component quantity", malformed["reason"])

    def test_reference_ambiguity_stops_the_report(self):
        with TemporaryDirectory() as temp:
            bill = Path(temp) / "bill.csv"
            bill.write_text("ParentSku,ChildSKU,ApprovedQuantity\n"
                            "KIT-710,GSK-004,4\nKIT-710,GSK-004,6\n", encoding="utf-8")
            result = run("--bom", bill)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("repeated reference key", result.stderr)

    def test_whole_bill_finds_omissions_with_source_record_and_unit(self):
        with unit_inputs("ApprovedUOM", "ProposedUOM", ["EA"], ["EA"]) as (bill, proposal):
            with bill.open("a", encoding="utf-8", newline="") as stream:
                csv.writer(stream).writerows([["KIT-710", "00017", "3", "EA"], ["KIT-720", "CLP-100", "2", "CS"]])
            result = run("--whole-bill", "--bom", bill, "--proposed", proposal)
            self.assertEqual(result.returncode, 0, result.stderr)
            matched, missing, other = csv.DictReader(StringIO(result.stdout))
            self.assertEqual((matched["record"], matched["approved_record"], matched["decision"]), ("1", "1", "MATCH"))
            self.assertEqual((missing["ChildSKU"], missing["record"], missing["approved_record"]), ("00017", "", "2"))
            self.assertEqual((missing["approved_quantity"], missing["proposed_quantity"], missing["decision"]), ("3", "", "REVIEW"))
            self.assertEqual((other["ParentSku"], other["proposed_uom"], other["approved_uom"]), ("KIT-720", "", "CS"))

    def test_named_scope_excludes_other_kits_and_retains_original_record_numbers(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "proposal.csv"
            path.write_text("ParentSku,ChildSKU,DisplayOrder,IsDefault,Quantity\n"
                            "KIT-720,CLP-100,1,0,1\nKIT-710,PIN-002,1,0,2\n"
                            "KIT-710,PIN-002,2,0,1\nKIT-710,UNKNOWN,3,0,1\n", encoding="utf-8")
            result = run("--kit", "KIT-710", "--proposed", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = list(csv.DictReader(StringIO(result.stdout)))
            self.assertEqual({r["ParentSku"] for r in rows}, {"KIT-710"})
            self.assertEqual([r["record"] for r in rows], ["2", "3", "4", "", "", ""])
            self.assertEqual([r["approved_record"] for r in rows], ["1", "1", "", "2", "3", "4"])
            self.assertIn("more than once", rows[0]["reason"])
            self.assertIn("Pair absent", rows[2]["reason"])
            self.assertTrue(all(r["decision"] == "REVIEW" for r in rows))
            both = run("--kit", "KIT-710", "--kit", "KIT-720", "--proposed", path)
            self.assertEqual(both.stdout, run("--whole-bill", "--proposed", path).stdout)
            self.assertEqual(run("--kit", "kit-710", "--proposed", path).returncode, 2)
            self.assertEqual(run("--whole-bill", "--kit", "KIT-710").returncode, 2)

    def test_empty_proposal_and_bill(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "proposal.csv"
            path.write_text("ParentSku,ChildSKU,DisplayOrder,IsDefault,Quantity\n", encoding="utf-8")
            result = run("--whole-bill", "--proposed", path)
            rows = list(csv.DictReader(StringIO(result.stdout)))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([r["approved_record"] for r in rows], ["1", "2", "3", "4", "5"])
            self.assertTrue(all(r["record"] == "" and r["decision"] == "REVIEW" for r in rows))
            bill = Path(temp) / "bill.csv"
            bill.write_text("ParentSku,ChildSKU,ApprovedQuantity\n", encoding="utf-8")
            result = run("--whole-bill", "--bom", bill)
            self.assertEqual(result.returncode, 2)
            self.assertIn("populated approved bill", result.stderr)

    def test_excel_export_preserves_unicode_and_existing_files(self):
        with unit_inputs("ApprovedUOM", "ProposedUOM", ["µm"], ["mm"]) as (bill, proposal):
            output = bill.with_name("buyer-review.csv")
            result = run("--whole-bill", "--bom", bill, "--proposed", proposal, "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            original = output.read_bytes()
            self.assertTrue(original.startswith(b"\xef\xbb\xbf"))
            row = next(csv.DictReader(StringIO(original.decode("utf-8-sig"))))
            self.assertEqual(row["approved_uom"], "µm")
            self.assertEqual(row["decision"], "REVIEW")
            self.assertEqual(run("--output", output).returncode, 2)
            self.assertEqual(output.read_bytes(), original)
