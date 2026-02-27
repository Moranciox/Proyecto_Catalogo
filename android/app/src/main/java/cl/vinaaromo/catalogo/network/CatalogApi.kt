package cl.vinaaromo.catalogo.network

import cl.vinaaromo.catalogo.model.Product
import retrofit2.http.GET
import retrofit2.http.Query

interface CatalogApi {
    @GET("/products")
    suspend fun getProducts(
        @Query("q") q: String? = null,
        @Query("limit") limit: Int = 200,
        @Query("offset") offset: Int = 0
    ): List<Product>
}
