package cl.vinaaromo.catalogo.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
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
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
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

            Text(product.desc_producto, style = MaterialTheme.typography.titleLarge)

            Spacer(Modifier.height(10.dp))

            val priceText = product.precio_neto?.let { formatCLP(it) } ?: "—"

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("Precio neto", style = MaterialTheme.typography.labelMedium)
                    Text(priceText, style = MaterialTheme.typography.titleMedium)
                }

                Column {
                    Text("Código", style = MaterialTheme.typography.labelMedium)
                    Text("${product.cod_producto}", style = MaterialTheme.typography.titleMedium)
                }
            }

            Spacer(Modifier.height(12.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                if (product.is_featured) {
                    AssistChip(onClick = {}, label = { Text("Destacado") })
                }
                if (!product.is_active) {
                    AssistChip(onClick = {}, label = { Text("Desactivado") })
                }
            }

            if (!product.notes.isNullOrBlank()) {
                Spacer(Modifier.height(14.dp))
                Text("Notas", style = MaterialTheme.typography.titleSmall)
                Spacer(Modifier.height(6.dp))
                Text(product.notes!!, style = MaterialTheme.typography.bodyMedium)
            }

            Spacer(Modifier.height(12.dp))
        }
    }
}

private fun formatCLP(value: Double): String {
    val nf = NumberFormat.getCurrencyInstance(Locale("es", "CL"))
    nf.maximumFractionDigits = 0
    nf.minimumFractionDigits = 0
    return nf.format(value)
}
