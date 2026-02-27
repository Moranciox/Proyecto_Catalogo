package cl.vinaaromo.catalogo.storage

import android.content.Context
import java.io.File

object ImageStore {
    private fun imagesDir(context: Context): File {
        val dir = File(context.filesDir, "images")
        if (!dir.exists()) dir.mkdirs()
        return dir
    }

    fun productImageFile(context: Context, codProducto: Int): File {
        return File(imagesDir(context), "product_${codProducto}.jpg")
    }
}
