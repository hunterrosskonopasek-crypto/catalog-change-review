# Review a university hosted price catalog

A university buyer orders 400 empty vials. Both catalog versions quote $24 per box. The approved box holds 100 vials, so four boxes cost $96. The proposed box holds 80, so five boxes cost $120. A price-only comparison misses the $24 difference.

JAGGAER asks suppliers in its Science Catalog to offer scientific products, have 10,000 SKUs or fewer, keep product and pricing information current, and honor the prices they list. This independent example uses fictional items, prices and agreements. [JAGGAER Science Catalog supplier requirements](https://www.jaggaer.com/science-catalog)

STEMCELL Technologies describes quarterly price-file submissions for its hosted catalogs. If your institution also receives periodic files, keep the last approved export and review the proposed file against it before the next upload. [STEMCELL’s static-file workflow](https://www.stemcell.com/eprocurement-solutions-for-labs)

## Review a file before the next upload

[Open the hosted catalog price review](https://hunterworkflowconsulting.com/hosted-price-review) to run the example or select three UTF-8 CSVs on your device. Set the number of individual items needed in one order. The tool rounds each catalog up to whole order units and reports the two totals, their difference and any proposed fields that conflict with the effective agreement. The five example SKUs produce four items for review and one match. A blank pack count stays open even when both catalog files have the same blank.

For offline use, [download the HTML file](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/raw/refs/heads/main/examples/university-hosted-catalog/hosted-price-review.html) and open it in a browser. Each of the three files can contain up to 25 data records. The review CSV includes source record numbers and the agreement reference. Only follow the managed-pilot link if you want to contact HWC.

## Compare the supplier exports

Read [the approved catalog](approved.csv), [the proposed catalog](proposed.csv) and [the applicable price terms](price-terms.csv) together. Each price is in USD for one order unit. EA means each, BX means box and CS means case. The pack count is the total number of individual items per order unit. Assume the same buyer, supplier, product, currency and freight terms across both exports.

Divide each order-unit price by its pack count, then compare the proposed order unit and price with the applicable agreement.

| SKU | Approved → proposed | USD per individual item | Buyer decision |
| --- | --- | --- | --- |
| LBL-010 · blank labels | $12 / box of 100 → $120 / case of 1,000 | $0.12 → $0.12 | Keep the agreed box available or obtain approval for case orders. A quantity-one order costs $108 more and delivers 900 more labels. |
| BOX-020 · freezer box | $4.00 each → $4.40 each | $4.00 → $4.40 | Accept the 10% increase. Amendment B authorizes this exact price for the proposed catalog. |
| VIAL-030 · empty vial | $24 / box of 100 → $24 / box of 80 | $0.24 → $0.30 | Hold the change. The proposed pack raises cost per vial by 25%. The agreement specifies 100. |
| DIV-040 · storage divider | $18 / case of 200 → $18 / case with count missing | $0.09 → unknown | Request the proposed case count before approving it. |
| TAG-050 · inventory tag | $9 / box in both files, both counts missing | unknown → unknown | Request a pack count and supporting terms. An unchanged blank needs review too. |

## Run the public CLI

From the repository root, run

```sh
sample=examples/university-hosted-catalog
python3 review.py "$sample/approved.csv" "$sample/proposed.csv"
python3 review.py "$sample/approved.csv" "$sample/proposed.csv" \
  --field selling_unit --field pack_qty --field price_usd
```

The default run flags records 1, 3 and 4 for changes to selling unit or pack count. Adding price flags record 2 as well. Record 5 has identical blanks, so neither run flags it. The CLI compares field text. The calculations above and the agreement check are separate review steps.

For a live supplier export, HWC’s $750 managed pilot covers one product family and up to 500 source rows. Bring the family name, approximate row count and review deadline. [Scope the $750 catalog pilot](https://hunterworkflowconsulting.com/data-audits?utm_source=github&utm_medium=worked_example&utm_campaign=university_hosted_catalog#catalog)
