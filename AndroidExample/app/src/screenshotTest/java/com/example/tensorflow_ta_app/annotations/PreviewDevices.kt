package com.example.tensorflow_ta_app.annotations

import android.content.res.Configuration
import androidx.compose.ui.tooling.preview.Devices
import androidx.compose.ui.tooling.preview.Preview

// Phone – Pixel 6
 @Preview(name = "Pixel 6 - Light", device = Devices.PIXEL_6, uiMode = Configuration.UI_MODE_NIGHT_NO)
 @Preview(name = "Pixel 6 - Dark", device = Devices.PIXEL_6, uiMode = Configuration.UI_MODE_NIGHT_YES)

// Foldable
 @Preview(name = "Fold - Light", device = "id:pixel_fold", uiMode = Configuration.UI_MODE_NIGHT_NO)
 @Preview(name = "Fold - Dark", device = "id:pixel_fold", uiMode = Configuration.UI_MODE_NIGHT_YES)

// Tablet
 @Preview(name = "Tablet - Light", device = Devices.PIXEL_TABLET, uiMode = Configuration.UI_MODE_NIGHT_NO)
 @Preview(name = "Tablet - Dark", device = Devices.PIXEL_TABLET, uiMode = Configuration.UI_MODE_NIGHT_YES)

 annotation class PreviewDevices