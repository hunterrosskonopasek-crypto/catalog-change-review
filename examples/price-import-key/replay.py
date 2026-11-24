"""Compare two SQLite upsert keys using HWC's four fictional price records."""
import csv
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path


def prices():
    with Path(__file__).with_name("prices.csv").open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            cents = Decimal(row["usd_per_selling_unit"]) * 100
            if cents != cents.to_integral_value():
                raise ValueError("The fixture expects whole USD cents.")
            yield (row["price_list"], row["part_number"], row["selling_unit"], row["effective_date"],
                   int(row["pieces_per_selling_unit"]), int(cents))


def replay(records, key_columns):
    # Both runs get the same constraints and upsert. Only the primary key differs.
    key = ", ".join(key_columns)
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute(f"""CREATE TABLE prices (
            price_list TEXT NOT NULL, part_number TEXT NOT NULL,
            selling_unit TEXT NOT NULL CHECK (selling_unit IN ('carton', 'each')),
            effective_date TEXT NOT NULL, pieces INTEGER NOT NULL CHECK (pieces >= 1),
            price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
            PRIMARY KEY ({key})
        )""")
        db.executemany(f"""INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT ({key}) DO UPDATE SET
                price_list = excluded.price_list, selling_unit = excluded.selling_unit,
                effective_date = excluded.effective_date, pieces = excluded.pieces,
                price_cents = excluded.price_cents""", records)
        return db.execute("""SELECT price_list, part_number, selling_unit, effective_date, pieces, price_cents
                             FROM prices ORDER BY effective_date, selling_unit""").fetchall()


def main():
    rows = list(prices())
    sku_key = ("part_number",)
    price_key = ("price_list", "part_number", "selling_unit", "effective_date")
    collapsed = replay(rows, sku_key)
    kept = replay(rows, price_key)
    assert len(rows) == 4 and len(collapsed) == 1 and set(kept) == set(rows)
    assert collapsed[0][2:] == ("each", "2027-03-01", 1, 180)
    march_carton = next(row for row in kept if row[2:4] == ("carton", "2027-03-01"))
    assert march_carton[4:] == (20, 3200)
    assert replay(rows + rows, price_key) == kept
    assert replay(list(reversed(rows)), price_key) == kept
    assert replay(list(reversed(rows)), sku_key) != collapsed

    print(f"SKU key: {len(collapsed)} row. Three units at the surviving each price: ${3 * collapsed[0][5] / 100:.2f}.")
    print(f"Price key: {len(kept)} rows. Three March cartons of 20: ${3 * march_carton[5] / 100:.2f}.")


if __name__ == "__main__":
    main()
