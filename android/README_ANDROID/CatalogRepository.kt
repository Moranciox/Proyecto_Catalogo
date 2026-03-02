package YOUR_PACKAGE.data

import YOUR_PACKAGE.data.remote.CatalogApi
import YOUR_PACKAGE.data.dto.ProductsPageDto

class CatalogRepository(
    private val api: CatalogApi
) {
    suspend fun getProductsPage(
        page: Int,
        pageSize: Int,
        q: String?,
        includeInactive: Boolean
    ): ProductsPageDto = api.getProducts(
        page = page,
        pageSize = pageSize,
        q = q,
        includeInactive = includeInactive
    )
}
