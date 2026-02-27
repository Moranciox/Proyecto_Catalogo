package cl.vinaaromo.catalogo.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import cl.vinaaromo.catalogo.R
import cl.vinaaromo.catalogo.model.Product
import cl.vinaaromo.catalogo.storage.ImageStore
import coil.compose.AsyncImage
import coil.request.ImageRequest
import java.text.NumberFormat
import java.util.Locale
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.ui.graphics.vector.ImageVector


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductDetailScreen(product: Product, onBack: () -> Unit) {
    val context = LocalContext.current
    val imgFile = ImageStore.productImageFile(context, product.cod_producto)

    val imageModel = if (imgFile.exists()) imgFile else R.drawable.placeholder

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        product.desc_producto,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {

            // Imagen grande
            Card(Modifier.fillMaxWidth()) {
                AsyncImage(
                    model = ImageRequest.Builder(context)
                        .data(imageModel)
                        .crossfade(true)
                        .build(),
                    contentDescription = product.desc_producto,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(320.dp)
                )
            }

            Spacer(Modifier.height(16.dp))

            // Detalles
            Text(product.desc_producto, style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(8.dp))

            val priceText = product.precio_neto?.let { formatCLP(it) } ?: "—"
            Text("Precio neto: $priceText", style = MaterialTheme.typography.titleMedium)

            Spacer(Modifier.height(12.dp))

            if (product.is_featured) {
                AssistChip(onClick = {}, label = { Text("Destacado") })
                Spacer(Modifier.height(12.dp))
            }

            if (!product.notes.isNullOrBlank()) {
                Text("Notas:", style = MaterialTheme.typography.titleSmall)
                Text(product.notes!!, style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(12.dp))
            }

            // Si luego quieres más campos: unidad, grad, etc., aquí van.
            Text("Código: ${product.cod_producto}", style = MaterialTheme.typography.bodyMedium)
        }
    }
}

private fun formatCLP(value: Double): String {
    val nf = NumberFormat.getCurrencyInstance(Locale("es", "CL"))
    nf.maximumFractionDigits = 0
    nf.minimumFractionDigits = 0
    return nf.format(value)
}