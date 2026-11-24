# Wire price-basis worksheet

Use this worksheet when a wire quote lists a price per 1,000 feet and the catalog sells by the foot, cut length or roll. Enter the quoted amount, the number of feet it covers, the feet in one selling unit and the displayed price for that unit. Use prices for the same item, seller, date and commercial terms. The formulas run locally in your spreadsheet app.

[Download the editable Excel worksheet](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/raw/refs/heads/main/examples/wire-price-basis/wire-price-basis.xlsx)

## A 500-foot roll in a public bid

In McAllen ISD’s electrical supplies bid 2015-116, item 40 called for one 500-foot roll. One bidder quoted $74.69 per 1,000 feet and showed $37.35 per roll on the tabulation. The worksheet preserves the unrounded conversion, $74.69 × 500 ÷ 1,000 = $37.345, then rounds the selling-unit price to $37.35. Use your current quote for live orders. [Buyer tabulation, item 40](<https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/1469/Mcallenisd/4d71b4ac-4700-4c4a-855e-1064085002da/2015-116-Electrical-Tabs-by-Item.pdf?disposition=inline>)

Record the feet your customer receives for quantity one. A carton can contain several selling units. For example, Southwire’s November 2025 price sheet describes four 500-foot spools per carton for specified sizes and quotes prices per 1,000 feet. A distributor may sell one spool at a time. Check the actual selling terms before entering 500 or 2,000. [Manufacturer price sheet and packaging notes](<https://www.southwire.com/medias/Import-11132025-C.pdf?context=bWFzdGVyfHByaWNpbmctcGRmc3wxMjcxNjh8YXBwbGljYXRpb24vcGRmfGg0Mi9oZjMvOTQ4MjMzNTE5MTA3MC9JbXBvcnQgMTExMzIwMjUgQy5wZGZ8ZjJiMDg0N2E0MzZjOWU1ZDViZTJmODU1YjlkNzMwZjZjNGY5Mjk3NjllMzFiZGNiOTUxNzRlYmMwNGI3MTA4MA>)

A variance is a reason to check the source quote. Discounts, cutting, freight and tax can change the amounts being compared. The worksheet checks arithmetic and flags missing inputs. Your pricing owner decides whether to change a catalog or quote.

## When the same issue appears across a feed

The free browser diagnostic can check a sample for missing selling-unit fields. For an industrial catalog review, HWC’s $750 pilot covers up to 500 source rows and returns five worked examples. Start with the product family, row count and target review date. [Free 25-SKU diagnostic](https://hunterworkflowconsulting.com/free-25-sku-diagnostic?utm_source=github&utm_medium=worksheet&utm_campaign=wire_price_basis) · [Request the $750 pilot scope](https://form.jotform.com/263065301224041?q4_textarea2=I%20found%20HWC%20through%20the%20wire%20price-basis%20worksheet.%20I%20would%20like%20to%20scope%20the%20%24750%20diagnostic%20for%20up%20to%20500%20source%20rows.%20Product%20family%2C%20row%20count%20and%20target%20review%20date%3A%20)
