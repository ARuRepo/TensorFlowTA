package com.example.tensorflow_ta_app.testcases

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.android.tools.screenshot.PreviewTest
import com.example.tensorflow_ta_app.FirstView
import com.example.tensorflow_ta_app.LoginView
import com.example.tensorflow_ta_app.SecondView
import com.example.tensorflow_ta_app.ThirdView
import com.example.tensorflow_ta_app.ui.theme.TensorFlow_TA_AppTheme
import com.example.tensorflow_ta_app.annotations.PreviewDevices

/**
 * Compose preview tests to generate images of each view
 */
class PreviewTests {

    @PreviewTest
    @PreviewDevices
    @Composable
    fun LoginViewScreenshot() {
        TensorFlow_TA_AppTheme {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                LoginView(rememberNavController())
            }
        }
    }

    @PreviewTest
    @PreviewDevices
    @Composable
    fun FirstViewScreenshot() {
        TensorFlow_TA_AppTheme {
            Surface(
                modifier = Modifier.fillMaxSize(),
                color = MaterialTheme.colorScheme.background
            ) {
                FirstView(rememberNavController())
            }
        }
    }

    @PreviewTest
    @PreviewDevices
    @Composable
    fun SecondViewScreenshot() {
        TensorFlow_TA_AppTheme {
            TensorFlow_TA_AppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    SecondView(rememberNavController())
                }
            }
        }
    }

    @PreviewTest
    @PreviewDevices
    @Composable
    fun ThirdViewScreenshot() {
        TensorFlow_TA_AppTheme {
            TensorFlow_TA_AppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ThirdView(rememberNavController())
                }
            }
        }
    }
}