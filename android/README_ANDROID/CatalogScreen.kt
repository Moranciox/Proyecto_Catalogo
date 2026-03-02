package YOUR_PACKAGE.ui.catalog

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.itemsIndexed
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import YOUR_PACKAGE.data.dto.ProductDto

@Composable
fun CatalogScreen(
    state: CatalogUiState,
    onQueryChange: (String) -> Unit,
    onToggleInactive: (Boolean) -> Unit,
    onLoadMore: () -> Unit,
    onProductClick: (ProductDto) -> Unit,
) {
    Column(
        Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Catálogo", style = MaterialTheme.typography.headlineSmall)

        OutlinedTextField(
            value = state.query,
            onValueChange = onQueryChange,
            placeholder = { Text("Buscar por nombre o código") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Row(
            Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilterChip(
                selected = !state.includeInactive,
                onClick = { onToggleInactive(false) },
                label = { Text("Activos") }
            )
            FilterChip(
                selected = state.includeInactive,
                onClick = { onToggleInactive(true) },
                label = { Text("Todos") }
            )
            Spacer(Modifier.weight(1f))
            Text("${state.items.size}/${state.total}", style = MaterialTheme.typography.labelLarge)
        }

        if (state.error != null) {
            Text(state.error, color = MaterialTheme.colorScheme.error)
        }

        Box(Modifier.fillMaxSize()) {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(bottom = 16.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                itemsIndexed(state.items, key = { _, p -> p.codigo }) { idx, p ->
                    // TODO: Reemplaza por tu ProductCard real
                    ElevatedCard(
                        onClick = { onProductClick(p) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.padding(12.dp)) {
                            Text(p.nombre, maxLines = 2)
                            Spacer(Modifier.height(6.dp))
                            Text("CLP ${p.precio_neto}")
                        }
                    }

                    // Trigger load more cuando vas llegando al final
                    if (idx >= state.items.size - 8) {
                        LaunchedEffect(state.items.size, state.total) {
                            if (state.canLoadMore) onLoadMore()
                        }
                    }
                }
            }

            if (state.isLoading) {
                CircularProgressIndicator(Modifier.align(Alignment.Center))
            }
        }
    }
}
