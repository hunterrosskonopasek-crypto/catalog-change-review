"""Write a local Estuary catalog that compares two keys on the bundled CSV."""
import json
from operator import itemgetter

from replay import prices


FIELDS = ("price_list", "part_number", "selling_unit", "effective_date", "pieces", "price_cents")
PRICE_KEY = FIELDS[:4]
SCHEMA = {
    "type": "object",
    "properties": {
        "price_list": {"type": "string"},
        "part_number": {"type": "string"},
        "selling_unit": {"type": "string", "enum": ["carton", "each"]},
        "effective_date": {"type": "string", "format": "date"},
        "pieces": {"type": "integer", "minimum": 1},
        "price_cents": {"type": "integer", "minimum": 0},
    },
    "required": list(FIELDS),
    "reduce": {"strategy": "lastWriteWins"},
}


def collection(fields):
    return {"schema": SCHEMA, "key": ["/" + field for field in fields]}


def steps(name, events, expected):
    # One event per ingest step establishes the write order across transactions.
    sequence = [{"ingest": {"collection": name, "documents": [event]}} for event in events]
    sequence.append({"verify": {"collection": name, "documents": expected}})
    return sequence


def catalog():
    rows = [dict(zip(FIELDS, values)) for values in prices()]
    by_sku = "example/by-sku"
    by_price = "example/by-price"
    price_order = itemgetter(*PRICE_KEY)
    in_key_order = sorted(rows, key=price_order)
    march_carton = next(row for row in rows
                        if row["selling_unit"] == "carton" and row["effective_date"] == "2027-03-01")
    amended = dict(march_carton, price_cents=3350)
    after_amendment = [amended if row == march_carton else row for row in in_key_order]

    return {
        "collections": {by_sku: collection(["part_number"]), by_price: collection(PRICE_KEY)},
        "tests": {
            "example/test/sku-forward": steps(by_sku, rows, [rows[-1]]),
            "example/test/sku-reversed": steps(by_sku, rows[::-1], [rows[0]]),
            "example/test/price-key-reversed-replay": steps(by_price, rows + rows[::-1], in_key_order),
            "example/test/price-key-amendment": steps(by_price, rows + [amended], after_amendment),
        },
    }


if __name__ == "__main__":
    print(json.dumps(catalog(), indent=2))
