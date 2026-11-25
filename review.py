"""Compare two complete UTF-8 catalog snapshots from the same SKU namespace."""
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


def read_snapshot(path, key, fields, *, incomplete=None):
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
        for number, row in enumerate(rows, 1):
            if not row:
                continue
            if len(row) != len(headers):
                raise ValueError(f"A row has the wrong column count at data record {number}.")
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
            review_out=None, prior_review=None):
    if prior_review is not None and review_out is None:
        raise ValueError("--prior-review requires a new --review-out file.")
    keys = (key,) if isinstance(key, str) else tuple(key)
    if not keys or not fields or len(set((*keys, *fields))) != len(keys) + len(fields):
        raise ValueError("Choose distinct key columns and separate fields to compare.")
    key = keys[0] if len(keys) == 1 else keys
    left_incomplete = [] if review_out is not None else None
    right_incomplete = [] if review_out is not None else None
    left, left_blanks = read_snapshot(before, key, fields, incomplete=left_incomplete)
    right, right_blanks = read_snapshot(after, key, fields, incomplete=right_incomplete)
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
    try:
        report = compare(args.before, args.after, args.key or "sku", args.field or ("selling_unit", "pack_qty"),
                         review_out=args.review_out, prior_review=args.prior_review)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        message = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, UnicodeError) else "Could not read a valid UTF-8 CSV snapshot."
        print(message, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return int(args.fail_on_change and bool(report["findings"]))


if __name__ == "__main__":
    sys.exit(main())
