package YOUR_PACKAGE.ui.catalog

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import YOUR_PACKAGE.data.CatalogRepository
import YOUR_PACKAGE.data.dto.ProductDto
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class CatalogUiState(
    val query: String = "",
    val includeInactive: Boolean = false,
    val items: List<ProductDto> = emptyList(),
    val page: Int = 1,
    val pageSize: Int = 50,
    val total: Int = 0,
    val isLoading: Boolean = false,
    val error: String? = null
) {
    val canLoadMore: Boolean get() = items.size < total && !isLoading
}

class CatalogViewModel(
    private val repo: CatalogRepository
) : ViewModel() {

    private val _state = MutableStateFlow(CatalogUiState())
    val state: StateFlow<CatalogUiState> = _state

    private var searchJob: Job? = null

    init {
        refresh()
    }

    fun onQueryChange(q: String) {
        _state.update { it.copy(query = q) }
        // Debounce para no spamear el backend
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300)
            refresh()
        }
    }

    fun setIncludeInactive(v: Boolean) {
        _state.update { it.copy(includeInactive = v) }
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null, page = 1, items = emptyList()) }
            runCatching {
                repo.getProductsPage(
                    page = 1,
                    pageSize = _state.value.pageSize,
                    q = _state.value.query.trim().ifBlank { null },
                    includeInactive = _state.value.includeInactive
                )
            }.onSuccess { page ->
                _state.update {
                    it.copy(
                        items = page.items,
                        page = page.page,
                        total = page.total,
                        isLoading = false
                    )
                }
            }.onFailure { e ->
                _state.update { it.copy(isLoading = false, error = e.message ?: "Error") }
            }
        }
    }

    fun loadMore() {
        val s = _state.value
        if (!s.canLoadMore) return

        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            val nextPage = s.page + 1
            runCatching {
                repo.getProductsPage(
                    page = nextPage,
                    pageSize = s.pageSize,
                    q = s.query.trim().ifBlank { null },
                    includeInactive = s.includeInactive
                )
            }.onSuccess { page ->
                _state.update {
                    it.copy(
                        items = it.items + page.items,
                        page = page.page,
                        total = page.total,
                        isLoading = false
                    )
                }
            }.onFailure { e ->
                _state.update { it.copy(isLoading = false, error = e.message ?: "Error") }
            }
        }
    }
}
