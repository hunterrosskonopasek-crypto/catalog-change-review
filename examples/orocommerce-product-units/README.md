# Review selling units before an OroCommerce product import

A distributor sells labels individually and in cartons. It maps a single label to Oro’s `item` unit and a carton to `set`. The proposed product file changes a carton from 24 labels to 12. The USD price list still offers a set for $30 when a buyer orders at least five sets.

**Buying 120 labels as sets would cost $300 instead of $150.** Five approved sets × $30 cover 120 labels. The proposed conversion requires ten sets × $30 for the same 120. This calculation assumes the same effective price list, no intervening tier or promotion, and a buyer who selects sets. Oro prices each unit separately. It does not turn an order for 120 individual labels into an order for sets. [Oro product units and pricing](https://doc.oroinc.com/user/back-office/products/products/product-units/)

## Implementation partner handoff

Have a distributor migration with a product file due for import? Introduce Hunter to the catalog owner and the person approving the import. This note can be forwarded as written.

> Would a second review of one product family help before your next import? Hunter & Co. Workflow Consulting can compare your proposed catalog with approved source data. The prepaid pilot is $750 for up to 500 authorized source rows. You receive an editable list of findings and five worked examples with the supporting evidence. Your implementation team decides what to import. To scope it, send Hunter the product family, approximate source row count and planned import date. Please send only those details in the introduction. [Email Hunter](mailto:hunter@hunterworkflowconsulting.com?subject=Distributor%20catalog%20pilot%20introduction).

**What to have ready.** Once the data owner approves sharing and any required confidentiality agreement is in place, identify the approved supplier reference and the proposed export. For a pricing question, also identify the order unit, applicable price list and quantity tier. HWC records the conflicting values, links the supporting evidence and flags missing evidence for the catalog owner.

[See the $750 pilot scope](https://hunterworkflowconsulting.com/data-audits?utm_source=github&utm_medium=partner_handoff&utm_campaign=oro_product_unit_review#catalog) · [See five fictional review decisions below](#reproduce-the-comparison)

## Reproduce the comparison

The [approved units](approved-units.csv) and [proposed units](proposed-units.csv) are five fictional products projected onto the unit fields in Oro’s product CSV template. The [price-list extract](price-list.csv) uses the separate price-list headers and stays fixed in this exercise. These are review inputs. For a real import, obtain the target instance’s full template and use Oro’s **Validate** step. [Product import template](https://doc.oroinc.com/user/back-office/products/products/import-products/) · [Price-list import template](https://doc.oroinc.com/user/back-office/sales/price-lists/import/)

From the repository root, run

```sh
sample=examples/orocommerce-product-units
compare_units() {
  python3 review.py "$sample/approved-units.csv" "$1" \
  --field 'primaryUnitPrecision.unit.code' \
  --field 'primaryUnitPrecision.precision' \
  --field 'primaryUnitPrecision.conversionRate' \
  --field 'primaryUnitPrecision.sell' \
  --field 'additionalUnitPrecisions:0:unit:code' \
  --field 'additionalUnitPrecisions:0:precision' \
  --field 'additionalUnitPrecisions:0:conversionRate' \
  --field 'additionalUnitPrecisions:0:sell'
}
compare_units "$sample/proposed-units.csv" | diff -u "$sample/expected-findings.json" -
compare_units "$sample/reviewed-units.csv"
```

The first report matches [the checked output](expected-findings.json). Record numbers count data rows starting at 1 and exclude the header. The second report compares [the reviewed file](reviewed-units.csv) with the baseline and leaves one documented change, on record 4.

| Record / SKU | Proposed change | Evidence and decision |
| --- | --- | --- |
| 1 · LABEL-24 | Set conversion 24 → 12 items | The distributor’s fictional carton specification still says 24. Restore 24. The five-set tier applies to sets ordered, so the price file alone cannot catch this discrepancy. |
| 2 · CLIP-12 | Primary `item` sell flag 1 → 0 | The distributor still accepts individual orders. Restore 1. A $0.60 item price can remain in a list even when the product’s Sell setting hides that unit. |
| 3 · CAP-06 | Set quantity precision 0 → 1 | The warehouse ships sealed sets of six. Restore 0. A precision of 1 permits quantities in tenths, including 0.5 set. It does not mean there is one item per set. |
| 4 · RING-08 | Set conversion 8 → 10 items | The fictional signed packing revision approves ten rings per set and the existing $15 set price. Keep 10. Retain that approval with the import. |
| 5 · TRAY-04 | Unit fields unchanged | The supplied list shows only an item price. Check the customer’s effective price for a set before promising that price or concluding it is missing. |

For a customer review, verify the approved packaging revision, account, website, effective price list, currency, tiers and exact order unit. The CLI compares the product fields you pass. It does not look up the live store, compute prices or approve changes. The example has one additional unit per SKU. When source products have several, match them by unit code across exports before interpreting a difference in an indexed column such as `additionalUnitPrecisions:0:conversionRate`.

For one distributor, HWC’s $750 managed pilot reviews an authorized category of up to 500 source rows and returns an editable findings file plus five worked examples with source evidence. [Scope the $750 pilot](https://hunterworkflowconsulting.com/data-audits?utm_source=github&utm_medium=worked_example&utm_campaign=oro_product_unit_review#catalog)

## Recheck three fictional releases

Use the approved units file as the reference throughout. These commands select the same four fields across all three proposals. Each JSON file contains the SKUs and values under review.

```sh
sample=examples/orocommerce-product-units
track_units() {
  proposal=$1
  shift
  python3 review.py "$sample/approved-units.csv" "$sample/$proposal" \
    --field 'primaryUnitPrecision.sell' --field 'additionalUnitPrecisions:0:precision' \
    --field 'additionalUnitPrecisions:0:conversionRate' --field 'additionalUnitPrecisions:0:sell' "$@"
}
track_units proposed-units.csv --review-out first.json
```

In `first.json`, set RING-08’s `decision` to `Keep ten per set per packing revision A`. Then run

```sh
track_units reviewed-units.csv --prior-review first.json --review-out second.json
track_units next-proposal-units.csv --prior-review second.json --review-out third.json
```

In the second proposal, LABEL-24, CLIP-12 and CAP-06 match the approved data again. RING-08 still proposes ten per set, so the prior note carries forward. In the [third proposal](next-proposal-units.csv), RING-08 proposes eleven. Its earlier note appears in `previous_decision` and the new decision is blank. CLIP-12 reopens when the item sell flag returns to zero. TRAY-04 is a new finding because its proposed set now contains five items. The earlier question about its effective set price requires separate price evidence.
