package com.example.tensorflow_ta_app.tensorflow.models

import android.os.SystemClock
import android.util.Log
import androidx.test.platform.app.InstrumentationRegistry
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.gpu.CompatibilityList
import org.tensorflow.lite.gpu.GpuDelegate
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.image.TensorImage
import java.nio.FloatBuffer

open class TestingModel {

    private val threadCount = 4

    private val logTag = "TestingModel"
    private val context = InstrumentationRegistry.getInstrumentation().context

    data class PredictionResult(
        val predictions: List<Prediction>, val inferenceTime: Long
    )

    data class Prediction(val label: String, var score: Float)

    /**
     * Function which creates a LiteRT model
     * @param modelName the name of the model to load
     * @return Interpreter object to use for inference
     */
    internal fun createModel(
        modelName: String,
    ): Interpreter {

        val compatList = CompatibilityList()
        val modelFile = FileUtil.loadMappedFile(context, modelName)

        // Run using either GPU or if not available with the specified number of threads
        val options = Interpreter.Options().apply {
            if (compatList.isDelegateSupportedOnThisDevice) {
                val delegateOptions = compatList.bestOptionsForThisDevice
                this.addDelegate(GpuDelegate(delegateOptions))
            } else {
                this.setNumThreads(threadCount)
            }
        }
        Log.i(logTag, "Created the model $modelName")
        return Interpreter(modelFile, options)
    }

    /**
     * Function which returns the model input size
     * @param model the model to run the inference with
     * @return Int the size of the model input
     */
    internal fun getInputSize(model: Interpreter): Int {
        return model.getInputTensor(0).shape()[1]
    }

    /**
     * Function which runs inference with a model
     * @param model the model to run the inference with
     * @param state the current state as bitmap
     * @param labels a list of labels to use for labeling the results
     * @param task optional value for using a task when running inference
     * @return PredictionResult structure with the results
     */
    internal fun inference(
        model: Interpreter,
        state: TensorImage,
        labels: List<String>
    ): PredictionResult {

        var inferenceTime = SystemClock.uptimeMillis()

        // Setup the buffer to gather the outputs
        val outputShape = model.getOutputTensor(0)?.shape()
        val outputBuffer = FloatBuffer.allocate(outputShape?.get(1) ?: 0)
        outputBuffer.rewind()

        // Run inference
        model.run(state.buffer, outputBuffer)
        outputBuffer.rewind()

        // Retrieve output into the buffer
        val output = FloatArray(outputBuffer.capacity())
        outputBuffer.get(output)

        // Set the probability to zero if below threshold
        val outputList = output.map { it }

        // Add labels to categories
        val categories = labels.zip(outputList).map {
            Prediction(label = it.first, score = it.second)
        }.take(outputShape?.get(1) ?: 0)

        // Calculate inference time
        inferenceTime = SystemClock.uptimeMillis() - inferenceTime

        Log.i(logTag, "Inference executed in $inferenceTime ms")
        return PredictionResult(categories, inferenceTime)
    }
}