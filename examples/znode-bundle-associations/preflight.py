"""Review one bundle family offline against a product snapshot and an approved BOM."""
import argparse
from collections import Counter
import csv
from decimal import Decimal
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
RELATION = ("ParentSku", "ChildSKU")
FIELDS = ("record", *RELATION, "proposed_quantity", "approved_quantity", "decision", "reason")
UNIT_FIELDS = ("proposed_uom", "approved_uom")


def unit_header(headers, role, path):
    names = {"uom", "unit", "units", "unitofmeasure", "componentuom", "quantityunit",
             role + "uom", role + "unit", role + "unitofmeasure"}
    matches = [h for h in headers if re.sub(r"[\s_]+", "", h).lower() in names]
    if len(matches) > 1:
        raise ValueError(f"{path.name}: multiple quantity unit columns ({', '.join(matches)}). "
                         "Select one unit column and remove or rename the others.")
    return matches[0] if matches else None


def read_table(path, required, role=None):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        headers = next(reader, [])
        unit = unit_header(headers, role, path) if role else None
        if any(not h.strip() for h in headers) or len(set(headers)) != len(headers):
            raise ValueError(f"{path.name}: each header must be unique and nonblank")
        missing = set(required) - set(headers)
        if missing:
            raise ValueError(f"{path.name}: missing column(s) {', '.join(sorted(missing))}")
        rows = []
        for cells in reader:
            if not cells:
                continue
            if len(cells) != len(headers):
                raise ValueError(f"{path.name}: wrong cell count at line {reader.line_num}")
            rows.append(dict(zip(headers, cells)))
        return rows, unit


def index_reference(rows, keys, path):
    index = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        if any(not part.strip() for part in key) or key in index:
            raise ValueError(f"{path.name}: blank or repeated reference key {key!r}")
        index[key] = row
    return index


def number(text):
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", text):
        return None
    value = Decimal(text)
    return value if value.is_finite() and 1 <= value <= 99999 else None


def review_table(products_file, bill_file, proposed_file, *, whole_bill=False, kits=()):
    product_rows, _ = read_table(products_file, ["SKU", "ProductType"])
    products = index_reference(product_rows, ["SKU"], products_file)
    bill_rows, approved_column = read_table(bill_file, [*RELATION, "ApprovedQuantity"], "approved")
    bill = index_reference(bill_rows, RELATION, bill_file)
    selected = set(kits)
    if whole_bill and selected:
        raise ValueError("Choose the whole approved bill or specific kit IDs.")
    complete = whole_bill or bool(selected)
    if complete and not bill:
        raise ValueError(f"{bill_file.name}: completeness requires a populated approved bill")
    unknown = selected - {parent for parent, child in bill}
    if unknown:
        raise ValueError(f"{bill_file.name}: no approved components for requested kit(s) {sorted(unknown)!r}")
    bill_records = {pair: record for record, pair in enumerate(bill, 1)} if complete else {}
    for key, row in bill.items():
        if number(row["ApprovedQuantity"]) is None:
            raise ValueError(f"{bill_file.name}: confirm the approved quantity for {key!r}")
    proposal_fields = [*RELATION, "DisplayOrder", "IsDefault", "Quantity"]
    proposals, proposed_column = read_table(proposed_file, proposal_fields, "proposed")
    compare_units = bool(approved_column or proposed_column)
    result = []
    pairs = [(row["ParentSku"], row["ChildSKU"]) for row in proposals]
    frequency = Counter(pairs)
    for record, (row, pair) in enumerate(zip(proposals, pairs), 1):
        parent, child = pair
        if selected and parent not in selected:
            continue
        reasons = []
        if frequency[pair] > 1:
            reasons.append("Parent/child pair occurs more than once in proposal")
        parent_info = products.get((parent,))
        is_bundle = parent_info is not None and parent_info["ProductType"] == "BundleProduct"
        if parent_info is None:
            reasons.append("Parent SKU absent from supplied product snapshot")
        elif not is_bundle:
            reasons.append("Parent outside this bundle-only review")
        if (child,) not in products:
            reasons.append("Child SKU absent from supplied product snapshot")
        elif products[(child,)]["ProductType"] != "SimpleProduct":
            reasons.append("Child is not a simple product in supplied snapshot")
        if number(row["DisplayOrder"]) is None:
            reasons.append("Review display order against documented range 1-99999")
        if row["IsDefault"] not in ("0", "1"):
            reasons.append("IsDefault must be 0 or 1")
        raw = row["Quantity"]
        qty = number(raw)
        if not raw.strip() and is_bundle:
            reasons.append("Missing bundle component quantity")
        elif raw.strip() and qty is None:
            reasons.append("Review component quantity against documented range 1-99999")
        approved = bill.get(pair)
        if approved is None:
            reasons.append("Pair absent from supplied approved bill of materials")
        elif qty is not None and qty != number(approved["ApprovedQuantity"]):
            reasons.append("Proposed quantity differs from approved bill of materials")
        units = ()
        if compare_units:
            proposed_unit = row[proposed_column] if proposed_column else ""
            approved_unit = approved[approved_column] if approved and approved_column else ""
            units = (proposed_unit, approved_unit)
            if approved:
                if not proposed_unit.strip() or not approved_unit.strip():
                    reasons.append("Component unit missing from proposal or approved bill")
                elif proposed_unit.strip() != approved_unit.strip():
                    reasons.append("Component units differ. Confirm the unit or conversion with the kit owner")
        matched_reason = ("Matches supplied references, including component unit" if compare_units else
                          "Matches supplied IDs and quantity. Unit basis unverified")
        source = (bill_records.get(pair, ""),) if complete else ()
        result.append((record, parent, child, raw, approved["ApprovedQuantity"] if approved else "",
                       "REVIEW" if reasons else "MATCH", " | ".join(reasons) or matched_reason, *units, *source))
    fields = FIELDS + UNIT_FIELDS if compare_units else FIELDS
    if complete:
        fields += ("approved_record",)
        for pair, approved in bill.items():
            parent, child = pair
            if pair in frequency or (selected and parent not in selected):
                continue
            units = ("", approved[approved_column] if approved_column else "") if compare_units else ()
            result.append(("", parent, child, "", approved["ApprovedQuantity"], "REVIEW",
                           "Approved component absent from proposed import", *units, bill_records[pair]))
    return fields, result


def review(products_file, bill_file, proposed_file):
    """Yield review rows for callers that do not need the CSV headers."""
    yield from review_table(products_file, bill_file, proposed_file)[1]


def csv_cell(value):
    text = str(value)
    if text.startswith(("\t", "\r", "\n")) or text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def write_report(stream, fields, rows):
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(fields)
    writer.writerows([csv_cell(cell) for cell in row] for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--products", type=Path, default=HERE / "products.csv")
    parser.add_argument("--bom", type=Path, default=HERE / "approved-bom.csv")
    parser.add_argument("--proposed", type=Path, default=HERE / "proposed.csv")
    parser.add_argument("--output", type=Path,
                        help="Save to a new UTF-8 CSV with a byte-order mark for Excel.")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--whole-bill", action="store_true",
                       help="Review all proposed lines and flag any approved component omitted from the import.")
    scope.add_argument("--kit", action="append", default=[], metavar="PARENT_SKU",
                       help="Review the complete set of lines for this exact approved parent. Repeat for more kits.")
    args = parser.parse_args()
    try:
        fields, rows = review_table(args.products, args.bom, args.proposed,
                                    whole_bill=args.whole_bill, kits=args.kit)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        parser.exit(2, f"Input error: {exc}\n")
    try:
        if args.output is None:
            write_report(sys.stdout, fields, rows)
        else:
            stream = args.output.open("x", encoding="utf-8-sig", newline="")
            try:
                with stream:
                    write_report(stream, fields, rows)
            except (OSError, UnicodeError, csv.Error):
                args.output.unlink()
                raise
    except (OSError, UnicodeError, csv.Error) as exc:
        parser.exit(2, f"Output error: {exc}\n")


if __name__ == "__main__":
    main()
