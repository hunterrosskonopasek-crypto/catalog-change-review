# HWC Catalog Review for WordPress

[Try the plugin in WordPress Playground](https://playground.wordpress.net/?blueprint-url=https%3A%2F%2Fraw.githubusercontent.com%2Fhunterrosskonopasek-crypto%2Fcatalog-change-review%2Fmain%2Fwordpress%2Fblueprint.json) or [download version 1.1.0](https://github.com/hunterrosskonopasek-crypto/catalog-change-review/releases/download/wordpress-v1.1.0/hwc-catalog-review.zip). Upload the ZIP from Plugins → Add Plugin in an authorized WordPress installation.

Open **Tools → Catalog CSV Review**. Check the fictional sample or choose a UTF-8 CSV. The checker processes every record within the browser's documented resource limits. The first 100 findings appear on screen. Download the full text report or review worksheet. [Capabilities, limits and privacy](readme.txt)

Run `python wordpress/package.py` to build the installable ZIP. The build reuses the CSV parser, mappings, diagnostic rules and styles from the MIT-licensed offline sample checker and embeds readable code and hash-based Content Security Policy in a local page. WordPress supplies the menu and access check. Browser inputs never go to WordPress.

[Worked two-file WooCommerce import review](../examples/woocommerce-import/README.md)
