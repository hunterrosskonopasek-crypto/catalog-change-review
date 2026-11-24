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

## Test the same keys in Estuary Flow

The [catalog generator](flow_catalog.py) reads the same four rows and writes a self-contained Flow catalog. With Python 3 and [flowctl 0.6.16](https://github.com/estuary/flow/releases/tag/v0.6.16) on Linux or macOS, run these commands from the repository root.

```sh
python3 examples/price-import-key/flow_catalog.py > prices.flow.json
flowctl raw test --source prices.flow.json
```

Flow groups documents by the collection key when reducing them. Here each schema selects `lastWriteWins`, and each input arrives in its own transaction. A part-number key yields one reduced price. Reversing the transactions changes which price survives. The four-field key keeps all four offers in the reduced result even when the records arrive twice in opposite orders. A later correction to the March carton from $32.00 to $33.50 changes just that offer. Three March cartons then cost $100.50.

The local harness checks reduced collection contents in memory. Flow collections retain an append-only history. This exercise uses fictional inputs and performs no capture, external materialization or cloud publication. [Collection keys](https://docs.estuary.dev/concepts/collections/#keys) · [Upstream test harness](https://github.com/estuary/flow/blob/v0.6.16/crates/catalog-tests/README.md)

HWC created these rows for its [interactive price replay](https://hunterworkflowconsulting.com/contract-price-replay).
