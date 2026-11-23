=== Catalog Release Review ===
Contributors: hunterworkflow
Tags: csv, catalog, sku, woocommerce, import
Requires at least: 6.0
Tested up to: 7.1
Requires PHP: 7.4
Stable tag: 1.1.1
License: MIT
License URI: https://opensource.org/license/mit/

Review a catalog CSV before import. Check SKUs, barcodes, selling units, document links and related part numbers locally in your browser.

== Description ==

Open Tools > Catalog CSV Review and select a catalog export. Match the SKU and optional fields to the columns you use. The report lists the source record and suggested review for each finding. Download the complete results as a text file or an editable CSV with source values and space for the reviewer's decision.

Checks include missing or repeated exact SKUs, GTIN format and check digits, empty selling units, missing or malformed specification links, and mismatches between a related part number and its target. The checker never visits specification URLs. A valid barcode format does not establish product identity.

CSV files, their contents and the resulting reports stay in your browser. There are no accounts, remote services, telemetry, cookies or database writes from the checker. The tool changes no WordPress or WooCommerce product. Administrators and users with the WooCommerce management capability can use it. WooCommerce is optional.

== Installation ==

1. Install and activate Catalog Release Review.
2. Open Tools > Catalog CSV Review.
3. Choose Try a fictional sample or select a UTF-8 CSV with a header.
4. Match your columns, review the findings and download the worksheet.

Previous GitHub testers: deactivate HWC Catalog Review before installing this package under its new directory name. There is no saved catalog or configuration to migrate. If both are active, the new checker supplies the existing Tools menu item.

== Frequently Asked Questions ==

= How large a catalog can I check? =

All records in the selected file are checked. To keep memory use manageable on a browser tab, a file can be up to 4 MiB, 128 columns and 500,000 cells including its header. The screen shows the first 100 findings. Downloads include every finding up to 64 MiB per generated file. A larger report prompts you to split the source file. Keep repeated SKUs together when splitting if you need a duplicate comparison across rows.

= Which columns do I need? =

Select a selling SKU column. Barcode, unit, document URL and two part-number columns are optional. Match both part-number columns to run that comparison. The checker identifies skipped checks in the report.

= Will this import or repair my products? =

This is a review tool. Use your approved sources to decide which findings to resolve, then import using your normal workflow. When opening the worksheet in a spreadsheet, import identifier cells as text to preserve leading zeros.

== Changelog ==

= 1.1.1 =
* Adopted the directory name Catalog Release Review. The Tools menu remains available to people using the earlier GitHub edition.

= 1.1.0 =
* Review full CSV files within documented local memory limits. The preview shows up to 100 findings and both downloads retain the complete results.
* Added a directory readme and support for standard WordPress.org updates.

= 1.0.1 =
* Released the browser-local CSV sample checker and editable worksheet.
