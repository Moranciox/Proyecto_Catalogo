package YOUR_PACKAGE.data.dto

data class ProductDto(
    val codigo: Int,
    val nombre: String,
    val precio_neto: Int,
    val image_url: String? = null,
    val destacado: Boolean = false,
    val activo: Boolean = true,
    val notas: String? = null
)

data class ProductsPageDto(
    val items: List<ProductDto>,
    val page: Int,
    val page_size: Int,
    val total: Int
)
