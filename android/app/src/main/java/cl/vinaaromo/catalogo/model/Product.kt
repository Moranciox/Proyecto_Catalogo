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

    /**
     * Si un producto está desactivado (false), se puede ocultar del listado.
     * Por defecto es true para no romper compatibilidad con data antigua.
     */
    val is_active: Boolean = true,

    val sort_order: Int? = null,
    val notes: String? = null
)
