package cl.vinaaromo.catalogo.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun CatalogApp() {
    MaterialTheme {
        val nav = rememberNavController()
        NavHost(navController = nav, startDestination = NavRoutes.LIST) {
            composable(NavRoutes.LIST) {
                ProductListScreen(
                    onOpenDetail = { product ->
                        ProductDetailStore.current = product
                        nav.navigate(NavRoutes.DETAIL)
                    }
                )
            }
            composable(NavRoutes.DETAIL) {
                val p = ProductDetailStore.current
                if (p != null) ProductDetailScreen(product = p, onBack = { nav.popBackStack() })
            }
        }
    }
}