package cl.vinaaromo.catalogo.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import cl.vinaaromo.catalogo.R
import cl.vinaaromo.catalogo.model.Product
import cl.vinaaromo.catalogo.repo.CatalogRepository
import cl.vinaaromo.catalogo.storage.ImageStore
import coil.compose.AsyncImage
import coil.request.ImageRequest
import java.io.File
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ProductListScreen(onOpenDetail: (Product) -> Unit) {
    val repo = remember { CatalogRepository() }
    var products by remember { mutableStateOf<List<Product>>(emptyList()) }
    var query by remember { mutableStateOf("") }
    var featuredOnly by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        isLoading = true
        error = null
        runCatching { repo.fetchProducts(q = null, limit = 200, offset = 0) }
            .onSuccess { products = it }
            .onFailure { error = it.message ?: "Error desconocido" }
        isLoading = false
    }

    val filtered = remember(products, query, featuredOnly) {
        val q = query.trim()
        products
            .asSequence()
            .filter { if (featuredOnly) it.is_featured else true }
            .filter { if (q.isEmpty()) true else it.desc_producto.contains(q, ignoreCase = true) }
            .toList()
    }

    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Text("Catálogo Viña Aromo", style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(12.dp))

        OutlinedTextField(
            value = query,
            onValueChange = { query = it },
            label = { Text("Buscar") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(Modifier.height(8.dp))

        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            FilterChip(
                selected = featuredOnly,
                onClick = { featuredOnly = !featuredOnly },
                label = { Text("Destacados") }
            )
            Text("${filtered.size} productos", style = MaterialTheme.typography.labelLarge)
        }

        Spacer(Modifier.height(12.dp))

        when {
            isLoading -> CircularProgressIndicator()
            error != null -> Text("Error: $error", color = MaterialTheme.colorScheme.error)
            else -> {
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 170.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    modifier = Modifier.fillMaxSize()
                ) {
                    items(filtered, key = { it.cod_producto }) { p ->
                        ProductCard(product = p, onOpenDetail = onOpenDetail)
                    }
                }
            }
        }
    }
}

@Composable
private fun ProductCard(product: Product, onOpenDetail: (Product) -> Unit) {
    val context = LocalContext.current
    val imageFile: File = ImageStore.productImageFile(context, product.cod_producto)

    val model = if (imageFile.exists()) imageFile else R.drawable.placeholder

    ElevatedCard(
        modifier = Modifier.fillMaxWidth(),
        onClick = { onOpenDetail(product) }
    ) {
        Column(Modifier.padding(12.dp)) {
            AsyncImage(
                model = ImageRequest.Builder(context)
                    .data(model)
                    .crossfade(true)
                    .build(),
                contentDescription = product.desc_producto,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(120.dp)
            )

            Spacer(Modifier.height(10.dp))

            Text(
                product.desc_producto,
                style = MaterialTheme.typography.titleSmall,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(Modifier.height(8.dp))

            val priceText = product.precio_neto?.let { formatCLP(it) } ?: "—"
            Text(priceText, style = MaterialTheme.typography.titleMedium)

            Spacer(Modifier.height(8.dp))

            if (product.is_featured) {
                AssistChip(onClick = {}, label = { Text("Destacado") })
            }
        }
    }
}

private fun formatCLP(value: Double): String {
    val nf = NumberFormat.getCurrencyInstance(Locale("es", "CL"))
    nf.maximumFractionDigits = 0
    nf.minimumFractionDigits = 0
    return nf.format(value)
}