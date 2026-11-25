import contextlib
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

from review import compare, main


class ReleaseReviewTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.before = self.directory / "approved.csv"
        self.after = self.directory / "proposal.csv"

    def snapshot(self, path, pairs):
        with path.open("w", newline="", encoding="utf-8") as dest:
            writer = csv.writer(dest)
            writer.writerow(["sku", "value"])
            writer.writerows(pairs)

    def run_review(self, name, prior=None):
        path = self.directory / (name + ".json")
        compare(self.before, self.after, fields=["value"], review_out=path, prior_review=prior)
        return path, json.loads(path.read_text())

    def test_exact_keys_order_values_and_decisions(self):
        rows = [("01", "a"), ("1", "a"), (" 01", "a"), ("01 ", "a")]
        self.snapshot(self.before, rows)
        self.snapshot(self.after, [(sku, "b") for sku, _ in rows] + [("new", "x")])
        first, saved = self.run_review("first")
        for item in saved["items"]:
            item["decision"] = "note " + item["identifier"]
        first.write_text(json.dumps(saved))
        self.snapshot(self.before, rows[::-1])
        self.snapshot(self.after, [("01 ", "a"), (" 01", "different\nvalue"), ("1", "b"), ("01", "b")])
        second, current = self.run_review("second", first)
        by_key = {x["identifier"]: x for x in current["items"]}
        self.assertEqual((by_key["01"]["decision"], by_key["01"]["after_records"]), ("note 01", [4]))
        self.assertEqual(by_key["1"]["decision"], "note 1")
        self.assertEqual((by_key[" 01"]["status"], by_key[" 01"]["decision"]), ("changed", ""))
        self.assertEqual(by_key[" 01"]["previous_decision"], "note  01")
        self.assertEqual(by_key["01 "]["reason"], "matches_approved")
        self.assertEqual(by_key["new"]["reason"], "absent_from_both")
        self.snapshot(self.after, [("01 ", "b"), *rows[:-1]])
        _, third = self.run_review("third", second)
        reopened = next(x for x in third["items"] if x["identifier"] == "01 ")
        self.assertEqual((reopened["status"], reopened["decision"]), ("reopened", ""))

    def test_ambiguous_or_missing_identity(self):
        self.snapshot(self.before, [("A", "a"), ("B", "b")])
        self.snapshot(self.after, [("A", "x"), ("B", "y"), ("EXTRA", "z")])
        first, prior = self.run_review("first")
        for item in prior["items"]:
            item["decision"] = "previous note"
        first.write_text(json.dumps(prior))
        self.snapshot(self.after, [("A", "a"), ("A", "x"), ("  ", "y")])
        second, report = self.run_review("second", first)
        cases = {item["identifier"]: item for item in report["items"]}
        self.assertEqual((cases["A"]["reason"], cases["A"]["after_records"]), ("ambiguous_key", [1, 2]))
        self.assertEqual((cases["B"]["status"], cases["B"]["reason"]), ("identity_unresolved", "possible_incomplete_identity"))
        self.assertEqual((cases["EXTRA"]["status"], cases["EXTRA"]["reason"]), ("identity_unresolved", "identity_not_confirmed"))
        self.assertTrue(all(not x["decision"] for x in cases.values()))
        self.assertEqual(report["unidentified_rows"][0]["after_records"], [3])
        self.snapshot(self.after, [("A", "x"), ("B", "b")])
        _, report = self.run_review("third", second)
        cases = {item["identifier"]: item for item in report["items"]}
        self.assertEqual((cases["A"]["status"], cases["A"]["decision"]), ("new", ""))
        self.assertEqual(cases["EXTRA"]["reason"], "absent_from_both")

    def test_scope_validation_and_safe_output(self):
        self.snapshot(self.before, [("A", "x")])
        self.snapshot(self.after, [("A", "z")])
        first, original = self.run_review("first")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_review("first", first)
        self.assertEqual(original, json.loads(first.read_text()))
        self.snapshot(self.before, [("A", "y")])
        with self.assertRaisesRegex(ValueError, "same format"):
            self.run_review("other", first)
        self.snapshot(self.before, [("A", "x")])
        original["items"].append(original["items"][0])
        first.write_text(json.dumps(original))
        with self.assertRaisesRegex(ValueError, "repeated"):
            self.run_review("other", first)
        self.assertFalse((self.directory / "other.json").exists())

    def test_compound_key_carries_only_same_record_and_values(self):
        def snapshot(path, rows):
            with path.open("w", newline="", encoding="utf-8") as dest:
                writer = csv.writer(dest)
                writer.writerow(["vendor", "sku", "pack"])
                writer.writerows(rows)

        def review(name, prior=None, keys=("vendor", "sku")):
            path = self.directory / name
            compare(self.before, self.after, key=keys, fields=["pack"], review_out=path, prior_review=prior)
            return path, json.loads(path.read_text(encoding="utf-8"))

        approved = [("V|A", "01", "6"), ("V", "A|01", "6"), ("V", "01", "6"), ("V", "1", "6")]
        proposed = [(vendor, sku, "4") for vendor, sku, _ in approved]
        snapshot(self.before, approved)
        snapshot(self.after, proposed)
        first, saved = review("first.json")
        self.assertEqual(saved["scope"]["key"], ["vendor", "sku"])
        self.assertEqual(saved["counts"], {"new": 4})
        for item in saved["items"]:
            item["decision"] = "row " + str(item["before_records"][0])
        first.write_text(json.dumps(saved), encoding="utf-8")
        snapshot(self.before, approved[::-1])
        snapshot(self.after, [proposed[2], proposed[1], ("V|A", "01", "8"), proposed[3], proposed[3], ("V", " ", "4")])
        second, current = review("second.json", first)
        items = {tuple(item["identifier"]): item for item in current["items"]}
        self.assertEqual(items["V", "A|01"]["decision"], "row 2")
        self.assertEqual(items["V", "01"]["decision"], "row 3")
        self.assertEqual(items["V|A", "01"]["status"], "changed")
        self.assertEqual(items["V|A", "01"]["decision"], "")
        self.assertEqual(items["V", "1"]["reason"], "ambiguous_key")
        self.assertEqual(items["V", "1"]["decision"], "")
        self.assertEqual(current["unidentified_rows"][0]["after_records"], [6])
        with self.assertRaisesRegex(ValueError, "same format"):
            review("wrong-order.json", second, keys=("sku", "vendor"))

        saved["items"][0]["identifier"] = ["V", ""]
        first.write_text(json.dumps(saved), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "compound identifier"):
            review("bad-key.json", first)

    def test_partial_price_key_holds_only_compatible_additions_and_removals(self):
        header = "sku,date,price\n"
        self.before.write_text(header + "0007,March,32\n0008,March,34\n0009,,10\n", encoding="utf-8")
        self.after.write_text(header + "0009,April,10\n", encoding="utf-8")
        first = self.directory / "first.json"
        second = self.directory / "second.json"
        options = {"key": ("sku", "date"), "fields": ("price",)}
        compare(self.before, self.after, review_out=first, **options)
        saved = json.loads(first.read_text())
        for item in saved["items"]:
            if item["reason"] == "removed":
                item["decision"] = "Retire the March price"
        first.write_text(json.dumps(saved), encoding="utf-8")
        self.after.write_text(header + "0009,April,10\n0007, ,32\n", encoding="utf-8")
        compare(self.before, self.after, review_out=second, prior_review=first, **options)
        report = json.loads(second.read_text())
        items = {tuple(item["identifier"]): item for item in report["items"]}
        returned = items["0007", "March"]
        self.assertEqual((returned["status"], returned["decision"], returned["previous_decision"]),
                         ("identity_unresolved", "", "Retire the March price"))
        self.assertEqual(items["0008", "March"]["decision"], "Retire the March price")
        self.assertEqual(items["0009", "April"]["reason"], "possible_incomplete_identity")

        self.before.write_text(header + "0007,March,32\n0008,March,34\n0010,,10\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "same format"):
            compare(self.before, self.after, review_out=self.directory / "third.json", prior_review=second, **options)

    def test_four_column_price_example_through_cli(self):
        sample = Path(__file__).parent / "examples" / "price-import-key"
        args = [str(sample / "prices.csv"), str(sample / "proposed-prices.csv")]
        for key in ("price_list", "part_number", "selling_unit", "effective_date"):
            args.extend(("--key", key))
        out_file = self.directory / "private.json"
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = main([*args, "--field", "usd_per_selling_unit", "--fail-on-change", "--review-out", str(out_file)])
        self.assertEqual(result, 1)
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["counts"], {"changed": 1})
        self.assertEqual(report["findings"][0], {"reason": "changed", "before_records": [3], "after_records": [2],
                                                  "changed_columns": ["usd_per_selling_unit"]})
        self.assertNotIn("HWC-CLIP-20", stdout.getvalue())
        item = json.loads(out_file.read_text())["items"][0]
        self.assertEqual(item["identifier"], ["HWC-DEMO", "HWC-CLIP-20", "carton", "2027-03-01"])
        self.assertEqual((item["approved_values"], item["proposed_values"]), (["32.00"], ["1.80"]))

    def test_documented_oro_sequence_and_cli_privacy(self):
        sample = Path(__file__).parent / "examples" / "orocommerce-product-units"
        fields = ["primaryUnitPrecision.sell", "additionalUnitPrecisions:0:precision",
                  "additionalUnitPrecisions:0:conversionRate", "additionalUnitPrecisions:0:sell"]
        args = [str(sample / "approved-units.csv")]
        options = [arg for name in fields for arg in ("--field", name)]
        previous = None
        for i, (proposal, expected) in enumerate([
            ("proposed-units.csv", {"new": 4}),
            ("reviewed-units.csv", {"unchanged": 1, "closed": 3}),
            ("next-proposal-units.csv", {"changed": 1, "new": 1, "reopened": 1, "still_closed": 2}),
        ]):
            out = self.directory / (str(i) + ".json")
            prior = ["--prior-review", str(previous)] if previous else []
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main([*args, str(sample / proposal), *options, "--review-out", str(out),
                             "--fail-on-change", *prior])
            self.assertEqual(code, 1)
            self.assertNotIn("RING-08", stdout.getvalue())
            saved = json.loads(out.read_text())
            self.assertEqual(saved["counts"], expected)
            ring = next(item for item in saved["items"] if item["identifier"] == "RING-08")
            if i == 0:
                ring["decision"] = "Keep ten per set per packing revision A"
                out.write_text(json.dumps(saved))
            elif i == 1:
                self.assertEqual(ring["decision"], "Keep ten per set per packing revision A")
            else:
                self.assertEqual((ring["decision"], ring["previous_decision"]), ("", "Keep ten per set per packing revision A"))
            previous = out
