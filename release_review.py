"""Private, optional comparison of successive proposals against a fixed reference."""
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


ACTIVE = {"new", "unchanged", "changed", "reopened"}
CLOSED = {"closed", "still_closed"}
UNRESOLVED = "identity_unresolved"


def baseline_hash(groups, blanks, incomplete=None):
    # Record positions may change. Exact IDs, values, and multiplicity must agree.
    records = [(sku, sorted(row.fields for row in groups[sku])) for sku in sorted(groups)]
    content = [len(blanks), records]
    if incomplete is not None:
        content.append(sorted(incomplete))
    data = json.dumps(content, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def incomplete_key_index(rows):
    index = defaultdict(set)
    for components, _ in rows:
        present = tuple(i for i, value in enumerate(components) if value.strip())
        index[present].add(tuple(components[i] for i in present))
    return index


def could_match_incomplete(identifier, index):
    components = (identifier,) if isinstance(identifier, str) else identifier
    return any(tuple(components[i] for i in present) in values for present, values in index.items())


def load_prior(path, scope):
    if path is None:
        return {}
    with path.open(encoding="utf-8") as source:
        saved = json.load(source)
    if not isinstance(saved, dict) or saved.get("scope") != scope:
        raise ValueError("Previous review needs the same format, key, fields and approved baseline.")
    if not isinstance(saved.get("items"), list):
        raise ValueError("Previous review has no valid items list.")
    prior = {}
    for item in saved["items"]:
        if not isinstance(item, dict):
            raise ValueError("Invalid previous review item.")
        sku, state = item.get("identifier"), item.get("status")
        if isinstance(scope["key"], list):
            if (not isinstance(sku, list) or len(sku) != len(scope["key"]) or
                    not all(isinstance(value, str) and value.strip() for value in sku)):
                raise ValueError("Invalid compound identifier in the previous review.")
            sku = tuple(sku)
        elif not isinstance(sku, str) or not sku.strip():
            raise ValueError("Invalid identifier in the previous review.")
        if (sku in prior or
                not isinstance(state, str) or state not in ACTIVE | CLOSED | {UNRESOLVED} or
                not isinstance(item.get("decision"), str)):
            raise ValueError("Invalid or repeated identifier, status or decision in the previous review.")
        if state in ACTIVE:
            kind = item.get("reason")
            if kind not in ("changed", "added", "removed"):
                raise ValueError("Invalid previous review reason.")
            for side, absent in (("approved_values", kind == "added"), ("proposed_values", kind == "removed")):
                values = item.get(side)
                if (side not in item or (absent and values is not None) or
                        (not absent and (not isinstance(values, list) or len(values) != len(scope["fields"]) or
                                         not all(isinstance(value, str) for value in values)))):
                    raise ValueError("Invalid evidence in the previous review.")
        prior[sku] = item
    return prior


def write_new(path, report):
    # Publish only a complete file; a second writer or an existing input wins.
    temp = NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False)
    try:
        with temp:
            json.dump(report, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
        try:
            os.link(temp.name, path)
        except FileExistsError:
            raise ValueError("Review output already exists. Choose a new file.") from None
    finally:
        Path(temp.name).unlink()


def write_review(path, prior_path, key, fields, left, right, blanks, report, left_incomplete, right_incomplete):
    single_key = isinstance(key, str)
    scope = {"version": 1 if single_key else 2, "key": key if single_key else list(key),
             "fields": list(fields),
             "approved_sha256": baseline_hash(left, blanks, None if single_key else left_incomplete)}
    prior = load_prior(prior_path, scope)
    left_ids = {row.number: sku for sku, rows in left.items() for row in rows}
    right_ids = {row.number: sku for sku, rows in right.items() for row in rows}
    findings, missing = {}, []
    for finding in report["findings"]:
        if finding["reason"] == "missing_key":
            missing.append(finding)
            continue
        old = finding["before_records"]
        sku = left_ids[old[0]] if old else right_ids[finding["after_records"][0]]
        findings[sku] = finding

    uncertain_ids = bool(missing or report["counts"].get("ambiguous_key"))
    incomplete_before = incomplete_key_index(left_incomplete)
    incomplete_after = incomplete_key_index(right_incomplete)
    items = []
    for sku in dict.fromkeys((*findings, *prior)):
        finding = findings.get(sku)
        earlier = prior.get(sku, {})
        old_status = earlier.get("status")
        approved, proposed = left.get(sku, []), right.get(sku, [])
        item = {"identifier": sku, "before_records": [r.number for r in approved],
                "after_records": [r.number for r in proposed], "decision": ""}
        if finding and finding["reason"] == "ambiguous_key":
            item.update(status=UNRESOLVED, reason="ambiguous_key")
        elif finding and (
            (finding["reason"] == "removed" and could_match_incomplete(sku, incomplete_after)) or
            (finding["reason"] == "added" and could_match_incomplete(sku, incomplete_before))
        ):
            item.update(status=UNRESOLVED, reason="possible_incomplete_identity")
        elif finding:
            evidence = {"reason": finding["reason"],
                        "approved_values": list(approved[0].fields) if approved else None,
                        "proposed_values": list(proposed[0].fields) if proposed else None}
            if old_status in ACTIVE:
                same = all(earlier[k] == v for k, v in evidence.items())
                item["status"] = "unchanged" if same else "changed"
                if same:
                    item["decision"] = earlier["decision"]
            else:
                item["status"] = "reopened" if old_status in CLOSED else "new"
            item.update(evidence)
        elif not approved and not proposed and uncertain_ids:
            item.update(status=UNRESOLVED, reason="identity_not_confirmed")
        else:
            item["status"] = "still_closed" if old_status in CLOSED else "closed"
            item["reason"] = "matches_approved" if approved else "absent_from_both"
        if earlier.get("decision") and old_status in ACTIVE and item["status"] != "unchanged":
            item["previous_decision"] = earlier["decision"]
        items.append(item)
    counts = Counter(item["status"] for item in items)
    write_new(path, {"scope": scope, "counts": dict(sorted(counts.items())),
                     "items": items, "unidentified_rows": missing})
