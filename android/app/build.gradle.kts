plugins {
  id("com.android.application")
  id("org.jetbrains.kotlin.android")
  id("org.jetbrains.kotlin.plugin.serialization")
  id("org.jetbrains.kotlin.plugin.compose") // ✅
}

android {
  namespace = "cl.vinaaromo.catalogo"
  compileSdk = 34

  defaultConfig {
    applicationId = "cl.vinaaromo.catalogo"
    minSdk = 26
    targetSdk = 34
    versionCode = 1
    versionName = "1.0.0"
  }
  compileOptions {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
  }

  buildFeatures { compose = true }

  kotlinOptions { jvmTarget = "17" }

  packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

dependencies {
  implementation("androidx.core:core-ktx:1.13.1")
  implementation("androidx.activity:activity-compose:1.9.2")
  implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.6")
  implementation("androidx.compose.ui:ui:1.7.4")
  implementation("androidx.compose.ui:ui-tooling-preview:1.7.4")
  implementation("androidx.compose.material3:material3:1.3.0")
  implementation("androidx.navigation:navigation-compose:2.8.0")
  implementation("com.squareup.okhttp3:okhttp:4.12.0")
  implementation("com.squareup.retrofit2:retrofit:2.11.0")
  implementation("com.jakewharton.retrofit:retrofit2-kotlinx-serialization-converter:0.8.0")
  implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
  implementation("androidx.compose.material:material-icons-extended:1.7.4")

  implementation("io.coil-kt:coil-compose:2.7.0")

  debugImplementation("androidx.compose.ui:ui-tooling:1.7.4")
}
