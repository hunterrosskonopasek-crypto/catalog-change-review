<?php
/**
 * Plugin Name: HWC Catalog Review
 * Description: Review catalog CSVs for duplicate SKUs, selling units, barcodes, specification links and related part numbers before import.
 * Version: 1.1.0
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Author: Hunter & Co. Workflow Consulting
 * License: MIT
 * License URI: https://opensource.org/license/mit/
 * Text Domain: hwc-catalog-review
 */

defined( 'ABSPATH' ) || exit;

function hwc_catalog_review_capability() {
	return current_user_can( 'manage_woocommerce' ) ? 'manage_woocommerce' : 'manage_options';
}

function hwc_catalog_review_menu() {
	add_management_page(
		__( 'HWC Catalog Review', 'hwc-catalog-review' ),
		__( 'Catalog CSV Review', 'hwc-catalog-review' ),
		hwc_catalog_review_capability(),
		'hwc-catalog-review',
		'hwc_catalog_review_page'
	);
}
add_action( 'admin_menu', 'hwc_catalog_review_menu' );

function hwc_catalog_review_page() {
	if ( ! current_user_can( hwc_catalog_review_capability() ) ) {
		wp_die( esc_html__( 'You do not have permission to access this page.', 'hwc-catalog-review' ) );
	}
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Catalog CSV Review', 'hwc-catalog-review' ); ?></h1>
		<iframe title="<?php esc_attr_e( 'Local catalog CSV checker', 'hwc-catalog-review' ); ?>" src="<?php echo esc_url( plugins_url( 'catalog-review.html', __FILE__ ) ); ?>" sandbox="allow-scripts allow-downloads" width="100%" height="900" style="border:0"></iframe>
	</div>
	<?php
}
