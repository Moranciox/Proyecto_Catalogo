package cl.vinaaromo.catalogo.network

import cl.vinaaromo.catalogo.model.Product
import retrofit2.http.GET
import retrofit2.http.Query

interface CatalogApi {
    @GET("/products")
    suspend fun getProducts(
        @Query("q") q: String? = null,
        /**
         * Si es true, el backend también devuelve productos desactivados.
         * La app puede decidir si los muestra o no.
         */
        @Query("include_inactive") includeInactive: Boolean = false,
        // Si limit es null, el backend devuelve todo. Recomendado usar paginado.
        @Query("limit") limit: Int? = null,
        @Query("offset") offset: Int = 0
    ): List<Product>
}
