package cl.vinaaromo.catalogo.model

import kotlinx.serialization.Serializable

@Serializable
data class Product(
    val cod_producto: Int,
    val desc_producto: String,
    val precio_neto: Double? = null,

    // extras (EXT via backend)
    val image_filename: String? = null,
    val is_featured: Boolean = false,
    val sort_order: Int? = null,
    val notes: String? = null
)
