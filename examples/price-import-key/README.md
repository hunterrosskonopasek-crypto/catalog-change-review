# When a valid price feed loses its carton price

A distributor sells cable clip `HWC-CLIP-20` individually and in cartons of 20. The [four fictional price records](prices.csv) are valid for the same price list. Two selling units and two effective dates give four distinct prices.

| Effective date | Price per carton | Price per clip |
| --- | ---: | ---: |
| February 1, 2027 | $30.00 | $1.65 |
| March 1, 2027 | $32.00 | $1.80 |

## How one carton price can underbill $4,077

Suppose 45 customers each order three cartons at the March price in this example. Each order should bill $96.00. A part-number-only lookup that selects the $1.80 each price bills $5.40. That leaves $90.60 per order, or **$4,077 across 45 orders**, unbilled. The volume is hypothetical. This calculation measures invoice value and includes no retailer penalty or chargeback.

Before the next import, ask the release owner to choose one SKU sold both ways. Build a test order in the buyer’s usual customer group, select the carton explicitly, and compare the extended price with the approved price list for the order date. Repeat for one each. Record the source row and both totals so the reviewer can reproduce the result. Multiplying the each price by 20 would give $36.00 per carton here. The approved carton price is $32.00.

- [Screen up to 25 source rows in the free browser checker](https://hunterworkflowconsulting.com/free-25-sku-diagnostic?utm_source=github&utm_medium=field_note&utm_campaign=carton_price). The CSV stays on your device. Its unit and identifier flags can help you choose rows for the price test.
- For a paid review, bring one redacted approved price and its matching invoice line. Use the same SKU, selling unit, customer tier and effective date, then count distinct cartons invoiced on those terms. At the fictional $30.20 difference above, 165 cartons would represent $4,983.00 and 166 would represent $5,013.20. Your invoice history supplies the actual volume. [Check one invoice line privately on your device](https://hunterworkflowconsulting.com/free-25-sku-diagnostic?utm_source=github&utm_medium=field_note&utm_campaign=pricing_audit&utm_content=price_import_key#invoice-case-check). Enter a documented 12-month quantity only if you have one. [Request a written scope for the $1,500 pricing audit and read the refund terms](https://hunterworkflowconsulting.com/free-25-sku-diagnostic?utm_source=github&utm_medium=field_note&utm_campaign=pricing_audit&utm_content=price_import_key#pricing-leak-audit).
- [Install HWC Catalog Change Review from GitHub Marketplace](https://github.com/marketplace/actions/hwc-catalog-change-review). For the four-column price comparison below, use the [tested revision and installation instructions](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/blob/60f80401284794a284ccb98dd9f4984afd6e8ec1/README.md#use-in-github-actions).

## Reproduce the import

First, use the two exports to locate the difference a reviewer would have to explain.

### Compare two price exports

The [proposed feed](proposed-prices.csv) reorders the four records and assigns the March carton the individual clip’s price. From the repository root, use the current source checkout:

```sh
python3 review.py examples/price-import-key/prices.csv examples/price-import-key/proposed-prices.csv --key price_list --key part_number --key selling_unit --key effective_date --field usd_per_selling_unit
```

The one changed record moves from row 3 in the approved export to row 2 in the proposal. Its carton price moves from $32.00 to $1.80. Three cartons would total $5.40 against the approved $96.00. The March individual clip and both February records keep their prices.

To run this comparison in GitHub Actions, supply those four column names on successive lines of `key-columns` and set `compare-columns` to `usd_per_selling_unit` on a revision that includes compound keys. Each duplicate full key or incomplete identifier still goes to review.

### Test the import in SQLite

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
