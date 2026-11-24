# When a valid price feed loses its carton price

A distributor sells cable clip `HWC-CLIP-20` individually and in cartons of 20. The [four fictional price records](prices.csv) are valid for the same price list. Two selling units and two effective dates give four distinct prices.

| Effective date | Price per carton | Price per clip |
| --- | ---: | ---: |
| February 1, 2027 | $30.00 | $1.65 |
| March 1, 2027 | $32.00 | $1.80 |

## Reproduce the import

From the repository root, run the [Python and SQLite example](replay.py). It uses Python 3.8 or later with SQLite 3.24 or later, reads the bundled CSV, and creates two in-memory tables.

```sh
python3 examples/price-import-key/replay.py
```

```text
SKU key: 1 row. Three units at the surviving each price: $5.40.
Price key: 4 rows. Three March cartons of 20: $96.00.
```

Both tables accept every input row. With `PRIMARY KEY (part_number)`, the second row updates the first, and the remaining rows update that same record. In file order, the March single-clip price arrives last. A lookup that uses only the SKU and multiplies by an order quantity of three returns $5.40, even when the customer requested three cartons. The stored row itself says `each`.

With `PRIMARY KEY (price_list, part_number, selling_unit, effective_date)`, all four rows survive. The March carton row quotes $32.00, so three cartons total $96.00. The script also reimports and reverses the feed. Both operations preserve all four prices with this key. Reversing the feed changes which price survives with the SKU key. [SQLite UPSERT](https://sqlite.org/lang_upsert.html)

Estuary documents the same design question for collections. Its schema describes valid documents, and its key groups them using one or more JSON pointers. For this fixture, those pointers would be `[/price_list, /part_number, /selling_unit, /effective_date]`. This demonstration runs in local SQLite. [Estuary collection keys](https://docs.estuary.dev/concepts/collections/#keys)

HWC created these rows for its [interactive price replay](https://hunterworkflowconsulting.com/contract-price-replay).
