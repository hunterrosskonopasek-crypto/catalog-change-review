"""Pre-Import CI/CD Gate for B2B PIM & ERP Feeds. Compare two complete UTF-8 catalog snapshots."""
import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Record:
    number: int
    fields: tuple


# Only explicit ERP identifiers qualify. Generic SKU, vendor and ID columns also
# occur in single-system exports and do not establish a cross-system schema.
ERP_IDENTIFIERS = {
    "sap_material_number": "sap",
    "netsuite_internal_id": "netsuite",
    "acumatica_inventory_id": "acumatica",
    "odoo_product_id": "odoo",
    "dynamics_item_number": "dynamics",
}
ERP_LABELS = {"sap erp": "sap", "oracle netsuite": "netsuite", "microsoft dynamics": "dynamics"}


def read_snapshot(path, key, fields, *, incomplete=None, erp_systems=None):
    keys = (key,) if isinstance(key, str) else tuple(key)
    groups = defaultdict(list)
    blanks = []
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        rows = csv.reader(source, strict=True)
        headers = next(rows, [])
        if not headers or any(not h.strip() for h in headers) or len(set(headers)) != len(headers):
            raise ValueError("Each file needs unique, nonblank column names.")
        if any(name not in headers for name in (*keys, *fields)):
            raise ValueError("A required column is missing from a snapshot.")
        key_indices = [headers.index(name) for name in keys]
        indices = [headers.index(name) for name in fields]
        erp_indices = []
        if erp_systems is not None:
            for index, header in enumerate(headers):
                name = "_".join(header.lower().strip().split())
                if name in ERP_IDENTIFIERS:
                    erp_systems.add(ERP_IDENTIFIERS[name])
                elif name in ("source_erp", "erp_system"):
                    erp_indices.append(index)
        for number, row in enumerate(rows, 1):
            if not row:
                continue
            if len(row) != len(headers):
                raise ValueError(f"A row has the wrong column count at data record {number}.")
            if erp_indices and len(erp_systems) < 2:
                for index in erp_indices:
                    label = row[index].strip().casefold()
                    if label and label not in ("unknown", "n/a", "none"):
                        erp_systems.add(ERP_LABELS.get(label, label))
            components = tuple(row[i] for i in key_indices)
            if any(not value.strip() for value in components):
                blanks.append(number)
                if incomplete is not None:
                    incomplete.append((components, tuple(row[i] for i in indices)))
            else:
                identifier = components[0] if len(keys) == 1 else components
                groups[identifier].append(Record(number, tuple(row[i] for i in indices)))
    return groups, blanks


def compare(before, after, key="sku", fields=("selling_unit", "pack_qty"), *,
            review_out=None, prior_review=None, erp_systems=None):
    if prior_review is not None and review_out is None:
        raise ValueError("--prior-review requires a new --review-out file.")
    keys = (key,) if isinstance(key, str) else tuple(key)
    if not keys or not fields or len(set((*keys, *fields))) != len(keys) + len(fields):
        raise ValueError("Choose distinct key columns and separate fields to compare.")
    key = keys[0] if len(keys) == 1 else keys
    left_incomplete = [] if review_out is not None else None
    right_incomplete = [] if review_out is not None else None
    left, left_blanks = read_snapshot(before, key, fields, incomplete=left_incomplete, erp_systems=erp_systems)
    right, right_blanks = read_snapshot(after, key, fields, incomplete=right_incomplete, erp_systems=erp_systems)
    findings = []

    def add(kind, old_rows, new_rows, changed=()):
        findings.append(dict(reason=kind, before_records=old_rows, after_records=new_rows, changed_columns=list(changed)))

    for number in left_blanks:
        add("missing_key", [number], [])
    for number in right_blanks:
        add("missing_key", [], [number])
    for identifier in dict.fromkeys((*left, *right)):
        old = left.get(identifier, [])
        new = right.get(identifier, [])
        old_nums = [r.number for r in old]
        new_nums = [r.number for r in new]
        if len(old) > 1 or len(new) > 1:
            add("ambiguous_key", old_nums, new_nums)
        elif not old:
            add("added", [], new_nums)
        elif not new:
            add("removed", old_nums, [])
        elif old[0].fields != new[0].fields:
            changed = [field for i, field in enumerate(fields) if old[0].fields[i] != new[0].fields[i]]
            add("changed", old_nums, new_nums, changed)
    report = {
        "before_records": sum(map(len, left.values())) + len(left_blanks),
        "after_records": sum(map(len, right.values())) + len(right_blanks),
        "counts": dict(sorted(Counter(f["reason"] for f in findings).items())),
        "findings": findings,
    }
    if review_out is not None:
        from release_review import write_review
        write_review(review_out, prior_review, key, fields, left, right, left_blanks, report,
                     left_incomplete, right_incomplete)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--key", action="append", help="Repeat in order for a multi-column key. Default: sku.")
    parser.add_argument("--field", action="append", help="Repeat for each compared column.")
    parser.add_argument("--fail-on-change", action="store_true", help="Exit with status 1 for any finding.")
    parser.add_argument("--review-out", type=Path, help="Write a new private, editable release review JSON file.")
    parser.add_argument("--prior-review", type=Path, help="Carry matching decisions from an earlier --review-out file.")
    args = parser.parse_args(argv)
    erp_systems = set()
    try:
        report = compare(args.before, args.after, args.key or "sku", args.field or ("selling_unit", "pack_qty"),
                         review_out=args.review_out, prior_review=args.prior_review, erp_systems=erp_systems)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        message = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, UnicodeError) else "Could not read a valid UTF-8 CSV snapshot."
        print(message, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    counts = report["counts"]
    key_errors = counts.get("missing_key", 0) + counts.get("ambiguous_key", 0)
    if key_errors > 50 or len(erp_systems) > 1:
        triggers = []
        if key_errors > 50:
            triggers.append(f"{key_errors} missing or ambiguous key findings")
        if len(erp_systems) > 1:
            triggers.append("multiple ERP systems identified")
        print("Pre-import review: " + " and ".join(triggers) + ".", file=sys.stderr)
        print("For source-backed decisions before this import: $750 Direct Catalog Review, "
              "up to 500 rows in five business days from the agreed start. "
              "https://hunterworkflowconsulting.com/data-audits#catalog", file=sys.stderr)
        print("For recurring release checks: Catalog Check Pro, $149/month. "
              "https://hwc-catalog-check-pro.marinegnome.chatgpt.site/", file=sys.stderr)
    return int(args.fail_on_change and bool(report["findings"]))


if __name__ == "__main__":
    sys.exit(main())
