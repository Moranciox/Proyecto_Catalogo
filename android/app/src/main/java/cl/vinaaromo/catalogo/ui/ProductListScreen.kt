package cl.vinaaromo.catalogo.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ElevatedCard
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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

private enum class StatusFilter { ACTIVE, ALL, INACTIVE }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductListScreen(onOpenDetail: (Product) -> Unit) {
    val repo = remember { CatalogRepository() }

    var products by remember { mutableStateOf<List<Product>>(emptyList()) }
    var query by remember { mutableStateOf("") }
    var featuredOnly by remember { mutableStateOf(false) }
    var statusFilter by remember { mutableStateOf(StatusFilter.ACTIVE) }

    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        isLoading = true
        error = null
        runCatching {
            // Pedimos también inactivos para poder filtrar en UI.
            repo.fetchProducts(q = null, includeInactive = true, limit = 200, offset = 0)
        }
            .onSuccess { products = it }
            .onFailure { error = it.message ?: "Error desconocido" }
        isLoading = false
    }

    val filtered = remember(products, query, featuredOnly, statusFilter) {
        val q = query.trim()

        products
            .asSequence()
            .filter { if (featuredOnly) it.is_featured else true }
            .filter {
                when (statusFilter) {
                    StatusFilter.ACTIVE -> it.is_active
                    StatusFilter.INACTIVE -> !it.is_active
                    StatusFilter.ALL -> true
                }
            }
            .filter { if (q.isEmpty()) true else it.desc_producto.contains(q, ignoreCase = true) }
            .sortedWith(
                compareBy<Product> { it.sort_order ?: Int.MAX_VALUE }
                    .thenBy { it.desc_producto.lowercase(Locale("es", "CL")) }
            )
            .toList()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Catálogo Viña Aromo", style = MaterialTheme.typography.titleLarge)
            Text("${filtered.size} productos", style = MaterialTheme.typography.labelLarge)
        }

        Spacer(Modifier.height(12.dp))

        OutlinedTextField(
            value = query,
            onValueChange = { query = it },
            label = { Text("Buscar") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            FilterChip(
                selected = featuredOnly,
                onClick = { featuredOnly = !featuredOnly },
                label = { Text("Destacados") }
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(
                    selected = statusFilter == StatusFilter.ACTIVE,
                    onClick = { statusFilter = StatusFilter.ACTIVE },
                    label = { Text("Activos") }
                )

                FilterChip(
                    selected = statusFilter == StatusFilter.ALL,
                    onClick = { statusFilter = StatusFilter.ALL },
                    label = { Text("Todos") }
                )

                FilterChip(
                    selected = statusFilter == StatusFilter.INACTIVE,
                    onClick = { statusFilter = StatusFilter.INACTIVE },
                    label = { Text("Desact.") }
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        when {
            isLoading -> {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                    CircularProgressIndicator()
                }
            }

            error != null -> {
                Text("Error: $error", color = MaterialTheme.colorScheme.error)
            }

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
            Card(Modifier.fillMaxWidth()) {
                AsyncImage(
                    model = ImageRequest.Builder(context)
                        .data(model)
                        .crossfade(true)
                        .build(),
                    contentDescription = product.desc_producto,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(140.dp)
                )
            }

            Spacer(Modifier.height(10.dp))

            Text(
                text = product.desc_producto,
                style = MaterialTheme.typography.titleSmall,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(Modifier.height(8.dp))

            val priceText = product.precio_neto?.let { formatCLP(it) } ?: "—"
            Text(
                text = priceText,
                style = MaterialTheme.typography.titleMedium
            )

            Spacer(Modifier.height(2.dp))

            Text(
                text = "Código: ${product.cod_producto}",
                style = MaterialTheme.typography.labelMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (product.is_featured) {
                    AssistChip(onClick = {}, label = { Text("Destacado") })
                }

                if (!product.is_active) {
                    AssistChip(onClick = {}, label = { Text("Desactivado") })
                }
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
