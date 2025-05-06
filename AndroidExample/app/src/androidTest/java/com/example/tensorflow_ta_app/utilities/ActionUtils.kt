package com.example.tensorflow_ta_app.utilities

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.os.SystemClock.sleep
import android.util.Log
import androidx.core.graphics.blue
import androidx.core.graphics.green
import androidx.core.graphics.red
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiSelector
import androidx.test.uiautomator.Until
import com.example.tensorflow_ta_app.data.TestData
import com.example.tensorflow_ta_app.data.TestData.TextData
import org.tensorflow.lite.DataType
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.io.File

/**
 * This class is for executing the different actions established by the models
 */
class ActionUtils {

    private val logTag = "ActionUtils"
    private val uiAutomator: UiDevice =
        UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    private val context = InstrumentationRegistry.getInstrumentation().targetContext
    private val actionDelay = 3000L

    /**
     * Function which launches an application based on package name
     * @param packageName the name of the package as string
     */
    fun launchApplication(packageName: String) {

        Log.i(logTag, "Launching the application $packageName")

        // Start from the home screen
        uiAutomator.executeShellCommand(
            "am start -n ${packageName}/${packageName}.MainActivity"
        )

        uiAutomator.wait(Until.hasObject(By.res("login_view_title")), actionDelay)
        sleep(actionDelay)
    }

    /**
     * Function which stops an application based on package name
     * @param packageName the name of the package as string
     */
    fun stopApplication(packageName: String) {

        Log.i(logTag, "Stopping the application $packageName")

        // Start from the home screen
        uiAutomator.executeShellCommand(
            "am stop -n ${packageName}/${packageName}.MainActivity"
        )

        sleep(actionDelay)
    }

    /**
     * Function which takes a screenshot and prepares it for inference as TensorImage
     * @param task optional value for using a task when running inference
     */
    fun captureState(inputSize: Int, task: Int? = null): TensorImage {

        Log.i(logTag, "Capturing a screenshot as state")
        uiAutomator.waitForIdle()

        val screenshotFile = File(context.filesDir, "state.png")
        uiAutomator.takeScreenshot(screenshotFile)

        // Load the screenshot as a bitmap and resize for faster processing
        var bitmap = BitmapFactory.decodeFile(screenshotFile.absolutePath)

        // Crop the top bar off the image
        val topCrop = (bitmap.height * 0.05f).toInt()
        bitmap = Bitmap.createBitmap(
            bitmap,
            0,
            topCrop,
            bitmap.width,
            bitmap.height - topCrop
        )

        // Resize the bitmap
        bitmap = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, false)

        // If there is a task defined the bitmap will be augmented
        task?.let {
            val mutableBitmap = bitmap.copy(Bitmap.Config.ARGB_8888, true)

            var prevRed = 0
            var prevGreen = 0
            var prevBlue = 0

            var augmentedRed = 0
            var augmentedGreen = 0
            var augmentedBlue = 0

            // Iterate through each pixel and modify its values
            for (x in 0 until inputSize) {
                for (y in 0 until inputSize) {
                    val pixel = mutableBitmap.getPixel(x, y)

                    // If matching, update the pixel value using the previous values
                    if (pixel.red == prevRed &&
                        pixel.green == prevGreen &&
                        pixel.blue == prevBlue
                    ) {
                        mutableBitmap.setPixel(
                            x,
                            y,
                            Color.rgb(augmentedRed, augmentedGreen, augmentedBlue)
                        )
                    } else {
                        // Add or subtract the value from each color channel
                        augmentedRed = augmentPixel(pixel.red + task)
                        augmentedGreen = augmentPixel(pixel.green + task)
                        augmentedBlue = augmentPixel(pixel.blue + task)

                        // Update the pixel value
                        mutableBitmap.setPixel(
                            x, y, Color.rgb(
                                augmentedRed,
                                augmentedGreen,
                                augmentedBlue
                            )
                        )
                    }

                    prevRed = pixel.red
                    prevGreen = pixel.green
                    prevBlue = pixel.blue
                }
            }
            bitmap = mutableBitmap
        }

        // Resize the bitmap
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(inputSize, inputSize, ResizeOp.ResizeMethod.BILINEAR))
            .build()

        // Create the tensor
        val tensorImage = TensorImage(DataType.FLOAT32)
        tensorImage.load(bitmap)
        return imageProcessor.process(tensorImage)
    }

    /**
     * Linear Congruential Generator which generates a pseudo random value for a pixel
     * @param seed the seed value for the random generator
     */
    private fun augmentPixel(seed: Int): Int {
        val a = 1664525L
        val c = 1013904223L
        val m = 2L shl 32
        return (((a * seed + c) % m) % 256).toInt()
    }

    /**
     * Function which swipes the screen
     * @param direction the direction of the swipe
     */
    fun swipe(direction: TestData.ActionData) {

        val screenWidth = uiAutomator.displayWidth
        val screenHeight = uiAutomator.displayHeight

        val screenCenterWidth = screenWidth / 2
        val screenCenterHeight = screenHeight / 2

        val verticalSteps = screenCenterHeight / 10

        if (direction == TestData.ActionData.SWIPE_UP) {

            Log.i(logTag, "Swiping up")

            uiAutomator.swipe(
                screenCenterWidth,
                screenCenterHeight,
                screenCenterWidth,
                0,
                verticalSteps
            )
        }

        if (direction == TestData.ActionData.SWIPE_DOWN) {

            Log.i(logTag, "Swiping down")

            uiAutomator.swipe(
                screenCenterWidth,
                screenCenterHeight,
                screenCenterWidth,
                screenHeight,
                verticalSteps
            )
        }

        sleep(actionDelay)
    }

    /**
     * Function which performs a login
     */
    fun performLogin() {

        val username = By.res("login_view_username")
        val password = By.res("login_view_password")

        if (uiAutomator.wait(Until.hasObject(username), actionDelay))
            uiAutomator.findObject(username).text = TextData.USERNAME_TEXT.value


        if (uiAutomator.wait(Until.hasObject(password), actionDelay))
            uiAutomator.findObject(password).text = TextData.PASSWORD_TEXT.value

        tapButton(TestData.ButtonData.LOGIN_BUTTON)
    }

    /**
     * Function which taps a button if it exists
     * @param button the button to tap from test data
     */
    fun tapButton(button: TestData.ButtonData) {
        val buttonObject = uiAutomator.findObject(UiSelector().text(button.value))

        if (buttonObject.waitForExists(actionDelay)) {
            Log.i(logTag, "Tapping ${button.value} -button")
            buttonObject.click()
            sleep(actionDelay)
            return
        }

        Log.i(logTag, "Failed tapping ${button.value} -button")
    }

    /**
     * Function which does nothing
     */
    fun standBy() {
        sleep(actionDelay)
    }

    /**
     * Function which resets by logging out
     */
    fun performReset() {
        Log.i(logTag, "Performing a reset")
        tapButton(TestData.ButtonData.LOGOUT_BUTTON)
    }
}