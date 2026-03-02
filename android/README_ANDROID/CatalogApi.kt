package YOUR_PACKAGE.data.remote

import YOUR_PACKAGE.data.dto.ProductsPageDto
import retrofit2.http.GET
import retrofit2.http.Query

interface CatalogApi {
    @GET("products")
    suspend fun getProducts(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int,
        @Query("q") q: String? = null,
        @Query("include_inactive") includeInactive: Boolean = false
    ): ProductsPageDto
}
