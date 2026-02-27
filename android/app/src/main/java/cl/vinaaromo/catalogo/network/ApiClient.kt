package cl.vinaaromo.catalogo.network

import com.jakewharton.retrofit2.converter.kotlinx.serialization.asConverterFactory
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import retrofit2.Retrofit

object ApiClient {
    // Emulador Android -> host del PC
    private const val BASE_URL = "http://192.168.4.181:8080"

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
            .build()
    }

    val api: CatalogApi by lazy { retrofit.create(CatalogApi::class.java) }
}
