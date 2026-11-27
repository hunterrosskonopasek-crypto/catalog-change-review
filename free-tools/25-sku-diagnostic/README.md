# Free 25-SKU diagnostic for offline use

[Download the offline diagnostic (ZIP)](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/raw/refs/heads/main/free-tools/25-sku-diagnostic/HWC-Free-25-SKU-Diagnostic.zip). Extract `HWC-Free-25-SKU-Diagnostic.html` and open it in a current desktop browser with JavaScript enabled. The ZIP contains one file. Once you have it, opening the tool, reading a CSV and saving either report all work offline.

1. Choose a UTF-8 CSV containing a header and 1–25 product rows, up to 512 KiB. A fictional sample and a downloadable CSV template are built in.
2. Select your SKU column if prompted. Under **Match optional columns**, select the barcode, selling unit, specification link and both related-card part-number columns available in your export. Fields you skip are identified in the report.
3. Select **Download report (.txt)** to save record numbers, findings and suggested checks. Record 1 is the first data row. The text summary omits your SKU and source values.
4. Select **Download review worksheet (.csv)** for one row per finding, including the selling SKU, source column and value, comparison fields when relevant, and spaces for a reviewer, decision and approved value. Import SKU and value columns as text to preserve leading zeros. A report with zero findings produces a worksheet containing only the headings. The built-in example produces a file named `HWC-fictional-25-SKU-review.csv`.
5. **Clear sample** clears the working data from the page. Downloaded copies remain on your device.

The screen flags blank or repeated exact SKUs, GTIN format and check-digit errors, missing selling units, missing or malformed specification addresses, and differences between supplied card and destination part numbers. The checker flags missing hosts, backslashes used in place of URL slashes, and incomplete percent escapes. A correctly formatted address still requires a source check to verify the document and its contents.

## Published files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| Offline ZIP | 8,932 | `dcba700dd8156e60e20956481f2160768369fe8f323dd136ac227c116e2e391c` |
| Extracted HTML | 23,832 | `4550e877cdbdd7e3ffc2a98a3cae55be3bd7057d74270a7aaa8d7044d6071a37` |

The [single-file HTML source](HWC-Free-25-SKU-Diagnostic.html) also contains its license notice. This free offline edition is distributed under [the repository’s MIT license](../../LICENSE).

## Where the checks come from

HWC adapted its public browser parser, diagnostic and sample template from the [hosted Free 25-SKU diagnostic](https://hunterworkflowconsulting.com/free-25-sku-diagnostic). The standalone edition embeds the code, interface, styles and template in one file. Its content security policy disables network connections. HWC originally adapted the row checks and report format from the following first-party assets. The current edition also validates the supplied specification address before a browser can silently repair it.

| Production asset | SHA-256 |
| --- | --- |
| [Shared CSV parser and SKU/GTIN checks](https://hunterworkflowconsulting.com/catalog-file-check.js) | `bd4ef3634f0b7c0fe222de5dfaf01ca8bff128bdc2ccd605a50b7d919d3b49c0` |
| [25-row diagnostic and report](https://hunterworkflowconsulting.com/free-25-sku-diagnostic.js) | `edb18a9d91ae6de3838419e121bf00c4b32715e82a1c2d87b34eef762f53b5df` |
| [Sample CSV template](https://hunterworkflowconsulting.com/free-25-sku-template.csv) | `87710436cb49aa3d5c64dfabd4453ce1642d339f8748ffd5552c15af2b64ea5a` |
