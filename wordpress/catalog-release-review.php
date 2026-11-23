<?php
/**
 * Plugin Name: Catalog Release Review
 * Description: Review catalog CSVs for duplicate SKUs, selling units, barcodes, specification links and related part numbers before import.
 * Version: 1.1.1
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Author: Hunter & Co. Workflow Consulting
 * License: MIT
 * License URI: https://opensource.org/license/mit/
 * Text Domain: catalog-release-review
 */

defined( 'ABSPATH' ) || exit;

function catalog_release_review_capability() {
	return current_user_can( 'manage_woocommerce' ) ? 'manage_woocommerce' : 'manage_options';
}

function catalog_release_review_menu() {
	// The earlier GitHub package registers this same Tools page at priority 10.
	remove_action( 'admin_menu', 'hwc_catalog_review_menu' );
	add_management_page(
		__( 'Catalog Release Review', 'catalog-release-review' ),
		__( 'Catalog CSV Review', 'catalog-release-review' ),
		catalog_release_review_capability(),
		'hwc-catalog-review',
		'catalog_release_review_page'
	);
}
add_action( 'admin_menu', 'catalog_release_review_menu', 9 );

function catalog_release_review_page() {
	if ( ! current_user_can( catalog_release_review_capability() ) ) {
		wp_die( esc_html__( 'You do not have permission to access this page.', 'catalog-release-review' ) );
	}
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Catalog CSV Review', 'catalog-release-review' ); ?></h1>
		<iframe title="<?php esc_attr_e( 'Local catalog CSV checker', 'catalog-release-review' ); ?>" src="<?php echo esc_url( plugins_url( 'catalog-review.html', __FILE__ ) ); ?>" sandbox="allow-scripts allow-downloads" width="100%" height="900" style="border:0"></iframe>
	</div>
	<?php
}
