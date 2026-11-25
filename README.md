# Catalog Change Review

Catch a case-pack change before a distributor imports its next feed. This tool compares two complete UTF-8 CSV snapshots from the same seller and flags new or removed SKUs, changed pack or selling-unit fields, blank keys, and keys that appear more than once. It runs with Python 3.8 or later using the standard library. Your files stay on the machine where you run it.

**Handing a Shopify feed back to a merchant?** [Inspect two example worksheets](https://hunterworkflowconsulting.com/agency-catalog-trial#worked). In a fictional 100-row export, a supplier reference supports changing one glass pack from six to four. A different variant has both four and twelve in its references and stays on the merchant’s decision list.

[Request scope and availability for the $1,250 white-label QA trial](https://form.jotform.com/263065301224041?q4_textarea2=I%20found%20HWC%20through%20the%20GitHub%20catalog-change-review%20tool.%20I%20would%20like%20to%20discuss%20the%20%241%2C250%20white-label%20catalog%20QA%20trial%20for%20one%20authorized%20merchant%20feed%2C%20up%20to%20100%20source%20rows%20and%2012%20manual%20cases.%20Product%20family%2C%20approximate%20row%20count%20and%20desired%20review%20date%3A%20). It covers one authorized merchant feed, one pack-count field, up to 100 source rows, 12 manual cases and one correction round. The form asks for the product family, approximate row count and review date. Share the export once both parties agree on scope and data sharing.

Have a small catalog sample? [Check up to 25 SKUs in your browser](https://hunterworkflowconsulting.com/free-25-sku-diagnostic?utm_source=github&utm_medium=readme&utm_campaign=catalog_change_review) to flag specification links, selling units and related-card model numbers for review. The CSV stays on your device. To use the same checks without an internet connection, [download the single-file offline edition (ZIP)](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/raw/refs/heads/main/free-tools/25-sku-diagnostic/HWC-Free-25-SKU-Diagnostic.zip) and open the extracted HTML in your browser. [Offline instructions and checksums](free-tools/25-sku-diagnostic/README.md). For a larger export, the [$750 managed pilot](https://hunterworkflowconsulting.com/data-audits?utm_source=github&utm_medium=readme&utm_campaign=catalog_change_review#catalog) covers one product category and up to 500 source rows. If one SKU has separate each and carton price rows, both count. Your catalog owner receives an editable findings file and five worked examples with source evidence.

[Audit related-product card descriptions](offers/related-product-card-audit.md) when a card points to one model and its teaser names another. One $2,500 payment covers 12 months of unlimited local runs for one licensed storefront. Renewal requires a new order.

[Compare industrial specifications and selling units](offers/broken-spec-missing-uom-auto-auditor.md) against your distributor reference files. One $2,500 payment covers 12 months of unlimited local audits of one licensed catalog. Renewal requires a new order.

Working with an Akeneo import? [Check incoming identifiers against an existing PIM export](https://hunterworkflowconsulting.com/akeneo-identifier-check?utm_source=github&utm_medium=readme&utm_campaign=catalog_change_review). Both files stay in your browser. The six-row example shows how a case change can update an existing product.

Check a distributor’s seasonal price break with [two real winter salt SKUs and a fictional staged order](examples/winter-catalog-check/README.md). At 49 bags, carrying the previous tier forward adds £13.72 before VAT.

Preparing a distributor kit import? [Try the eight-row kit check in your browser](https://hunterworkflowconsulting.com/bundle-bom-review?utm_source=github&utm_medium=readme&utm_campaign=distributor_kit_partner) or [run the Znode example offline](examples/znode-bundle-associations/README.md). The fictional kit calls for four gaskets, but the proposed file lists two. Implementation partners can [ask HWC to review an upcoming distributor release](https://form.jotform.com/263065301224041?q4_textarea2=GitHub%20Catalog%20Change%20Review%20%E2%80%94%20distributor%20kit%20release.%20I%20would%20like%20to%20discuss%20the%20%24750%20prepaid%20pilot%20for%20one%20authorized%20product%20family.%20Release%20or%20kit%20family%3A%20%0AApproximate%20source%20row%20count%3A%20%0APlanned%20import%20date%3A%20%0AWho%20reviews%20the%20findings%20%28role%29%3A%20). The $750 prepaid pilot covers one authorized product family of up to 500 source rows. A family or release name, approximate source row count, import date and reviewer’s role are enough to discuss scope. Keep customer names and files private at this stage.

Preparing a WooCommerce import? [Run a six-row variation and duplicate-SKU example](examples/woocommerce-import/README.md). Compare two fictional exports, then inspect the selling-unit mismatch in the [worked $750 migration QA pilot](https://hunterworkflowconsulting.com/shopify-plus-pim-agency-partner-program?utm_source=github&utm_medium=marketplace&utm_campaign=woocommerce_import_qa#woocommerce-migration-qa). HWC can review one authorized product family before the agency imports it.

Manufacturers can [compare the same part across up to three distributor exports](https://hunterworkflowconsulting.com/manufacturer-channel-comparison?utm_source=github&utm_medium=readme&utm_campaign=manufacturer_channel). For a plumbing feed, try the six-row flow-rating example. At 60 psi, 1.5 US gallons per minute equals 5.678117676 liters per minute. A listing rounded to 5.7 gets a precision check. A listing rated at 20 psi goes back to the reviewer for comparable evidence. The tool also exports missing parts and field conflicts. A [$3,000 managed review](https://hunterworkflowconsulting.com/manufacturer-channel-comparison#managed) adds source review, a correction list for each authorized channel and one recheck.

[Trace a pack mismatch from supplier to merchant to channel](examples/source-to-channel-feed/README.md). Five fictional SKUs show when to ask the catalog owner or the feed team for evidence, including a channel correction that masks a merchant discrepancy.

[Review a price change when four rows share a SKU](examples/price-import-key/README.md). Compare the exports by price list, part number, selling unit and effective date to find the March carton priced as one clip. The SQLite example shows the effect on a three-carton order.

## Try the example

WordPress agencies can [open the catalog checker inside WordPress Playground or install the plugin](wordpress/README.md) to review a CSV before import.

[Teach a 25-minute, two-CSV verification exercise](teaching/two-csv-check/README.md). Learners can use a spreadsheet or paper to trace a pack change, a repeated identifier and a missing value. The facilitator key includes the source records and the Python results.

[Download the v1.0.1 source ZIP](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/archive/refs/tags/v1.0.1.zip), unzip it and open the folder that contains `review.py`. Run the example from that folder.

```sh
python3 review.py examples/before.csv examples/after.csv
```

The example reports four review items. Before record 1 changes from six units per case to eight. After records 3 and 4 share a key, so that item needs a decision about its selling unit. One item was removed and one added. The tool outputs only record numbers, reason codes, and changed column names. The person reviewing the source decides which changes to approve.

[Five product identifiers from a grocery supplier table](examples/grocery-identifiers/README.md). Two six-bar packs share a description but carry different codes. The downloadable CSV shows which identifiers can be compared and which need supplier review.

[Check wire prices quoted per foot, roll or 1,000 feet](examples/wire-price-basis/README.md). The editable worksheet reconciles a public bid’s price for a 500-foot roll and can be used with your own quotes.

[Check cases versus individual units before quoting a group of supplies](examples/case-pack-bid-review/README.md). The editable worksheet compares a whole-case order with a piece-count estimate and flags the lines where the estimator needs a pack source or a pricing decision.

[Check an OroCommerce product import](examples/orocommerce-product-units/README.md) to see how a changed carton conversion can double the cost of 120 labels with every price-list row unchanged.

[Review a university hosted price catalog](examples/university-hosted-catalog/README.md) to distinguish an agreed price increase from a change in pack size or an unknown pack count.

[Compare two industrial tool feeds](examples/industrial-diameters/README.md). Run the sample to see why a rounded diameter can be accepted while a change to drill-point geometry needs a source check.

[Worked public-data example with USDA fruit catalogs](examples/usda-tefap/README.md). A comparison of 33 previous and 32 current rows separates packaging wording from an item missing in the new list.

## Use your exports

```sh
python3 review.py approved.csv proposed.csv --key item_id --field unit --field pack_size > review.json
```

The defaults are `sku`, `selling_unit`, and `pack_qty`. Names are case-sensitive. SKU matching preserves case, spaces and leading zeros. Quoted commas and embedded newlines are supported. Record numbers count CSV records after the header, including ignored empty records. Compare complete snapshots with matching coverage. A partial export will mark omitted items as removed.

## Recheck successive releases

For complete proposals covering the same catalog and approved reference, keep one private review per release. The current source checkout supports these options.

```sh
python3 review.py approved.csv proposed.csv --review-out first.json
python3 review.py approved.csv revised.csv --prior-review first.json --review-out second.json
```

In the first JSON file, edit only the `decision` string on a uniquely identified open item. Use the copy containing those notes as the next run’s prior review. Each new file records exact identifiers, selected values in the order shown under `scope.fields`, and current CSV record numbers. Store it with the authorized exports. The ordinary console report still omits identifiers and values. Choose a fresh output filename every time.

| Status | What the reviewer can conclude |
| --- | --- |
| `new` | A unique, reviewable difference appears for the first time or after identity was uncertain. |
| `unchanged` | The identifier, reason and selected before/after values match. The previous decision carries forward. |
| `changed` or `reopened` | Evidence changed or a previously closed difference returned. The new decision is blank. |
| `closed` or `still_closed` | The records now agree on the selected fields, or a formerly extra identifier is absent from both complete snapshots. The reason distinguishes these cases. |
| `identity_unresolved` | A duplicate key prevents a match, an incomplete key could explain an apparent addition or removal, or unidentified rows leave an earlier discrepancy uncertain. Consult the source before carrying a decision forward. |

Blank IDs are reported individually in `unidentified_rows` and never inherit a decision. Reordering rows is supported. A different key, field selection or approved keyed data starts a new review history. Changes outside the selected fields are outside the comparison. For a worked sequence, see the [fictional Oro unit releases](examples/orocommerce-product-units/README.md#recheck-three-fictional-releases).

For price lists with several records per SKU, repeat `--key` in the order agreed with the catalog owner. Choose stable identifiers. A change to a key component appears as a removed record and an added record. A blank component or repeated full key needs review. The private review stores each compound identifier as a JSON array and carries a decision only when the full identifier and selected evidence still match. [Worked four-column comparison](examples/price-import-key/README.md#compare-two-price-exports)

## Use in GitHub Actions

On a Linux runner with Python 3 and your repository already checked out, add this step. Paths point to the two snapshots in your workflow workspace.

```yaml
- name: Check catalog changes
  uses: hunterrosskonopasek-crypto/catalog-change-review@v1.0.1
  with:
    before: catalog/approved.csv
    after: catalog/proposed.csv
```

The action reports JSON and fails the step on any finding so a reviewer can decide whether to proceed. The local CLI exits successfully with findings unless you add `--fail-on-change`. Exit status 2 indicates invalid input.

Run the test suite with `python3 -m unittest -v`.

## When a change needs a human decision

If several people approve a feed, [try the two-lot packaging case](https://hunterworkflowconsulting.com/catalog-release-rehearsal) before choosing the [65-minute team rehearsal](https://hunterkonopasek.gumroad.com/l/catalog-release-rehearsal?utm_source=github&utm_medium=readme&utm_campaign=catalog_change_review&utm_content=team_rehearsal). The $1,000 kit includes 18 cases and scorecards for one internal team of up to 12.

The MIT license applies to this repository's original code. The USDA tables used in the public-data example are attributed alongside the extracts.
