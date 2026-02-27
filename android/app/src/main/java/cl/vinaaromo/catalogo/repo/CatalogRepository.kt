package cl.vinaaromo.catalogo.repo

import cl.vinaaromo.catalogo.model.Product
import cl.vinaaromo.catalogo.network.ApiClient

class CatalogRepository {
    suspend fun fetchProducts(q: String? = null, limit: Int = 200, offset: Int = 0): List<Product> {
        return ApiClient.api.getProducts(q = q, limit = limit, offset = offset)
    }
}