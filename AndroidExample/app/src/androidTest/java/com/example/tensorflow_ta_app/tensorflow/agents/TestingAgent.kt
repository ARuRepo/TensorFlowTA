package com.example.tensorflow_ta_app.tensorflow.agents

import android.util.Log
import com.example.tensorflow_ta_app.data.TestData
import com.example.tensorflow_ta_app.data.TestData.ActionData
import com.example.tensorflow_ta_app.tensorflow.models.TestingModel
import com.example.tensorflow_ta_app.utilities.ActionUtils

/**
 * This class is for calling the model specific classes to run inference and then handle the results
 */

class TestingAgent : TestingModel() {

    private val logTag = "TestingAgent"
    private val actionUtils = ActionUtils()
    private val taskLabels: List<String> = ActionData.entries.map { it.name }
    private val taskComplete = ActionData.TASK_COMPLETE
    private val inferenceLimit = 0.3f
    private val actionsLimit = 10
    private val navigationModel = createModel("navigation_model.tflite")
    private val assertModelsMap = mapOf(
        "LoginViewAssertData" to createModel("login_view_model.tflite"),
        "FirstViewAssertData" to createModel("first_view_model.tflite"),
        "SecondViewAssertData" to createModel("second_view_model.tflite"),
        "ThirdViewAssertData" to createModel("third_view_model.tflite")
    )

    /**
     * Function which navigates and asserts a view
     * @param navigationTask the current navigation task enumeration to execute
     * @param viewEntities list of enumeration values representing entities which are to be asserted
     * @return Boolean value whether the task is completed and state is asserted to match expectation
     */
    fun <T : Enum<T>> navigateAndAssert(
        navigationTask: TestData.NavigationData,
        viewEntities: List<T>
    ): Boolean {
        performNavigation(navigationTask)
        return assertViewEntities(viewEntities)
    }

    /**
     * Function which predicts an action using the navigation model
     * @param navigationTask the current navigation task enumeration to execute
     * @return true or false if the navigation task was completed successfully
     */
    fun performNavigation(navigationTask: TestData.NavigationData) {
        val taskName = TestData.NavigationData.entries[navigationTask.ordinal].name
        Log.i(logTag, "Starting to execute task $taskName")

        repeat(actionsLimit) {
            val state = actionUtils.captureState(
                getInputSize(navigationModel),
                navigationTask.ordinal
            )

            // Figure out which action to carry out
            val inference = inference(navigationModel, state, taskLabels)
            val maxScore = inference.predictions.maxByOrNull { it.score }

            Log.d(logTag, "Action predictions: ${inference.predictions}")

            // Get the action index based on prediction certainty
            val actionIndex = if (maxScore?.score!! >= inferenceLimit) {
                inference.predictions.indexOf(maxScore)
            } else {
                Log.i(logTag, "Task $taskName unable to establish an action!")
                taskComplete.ordinal
            }

            // Check if this action index indicates the task is complete
            if (actionIndex == taskComplete.ordinal) {
                Log.i(logTag, "Task $taskName execution complete!")
                return
            }

            // Get the action name
            val actionName = ActionData.entries[inference.predictions.indexOf(maxScore)]


            Log.i(logTag, "Action to execute $actionName")

            // Perform an action based on what the model suggests
            ActionData.entries[actionIndex].execute()
        }

        Log.i(logTag, "Ran out of actions executing task: $taskName")
        return
    }

    /**
     * Function which returns true or false based on whether the current view entities are asserted
     * @param viewEntities list of enumeration values representing entities which are to be asserted
     * @return Boolean value whether the state is asserted to match expectation
     */
    fun <T : Enum<T>> assertViewEntities(viewEntities: List<T>): Boolean {

        // Fetch the assert enumeration class
        val enumClass = viewEntities.first()::class.java

        // Create the model instance by selecting the correct one
        val assertModel = assertModelsMap[enumClass.simpleName]
        if (assertModel == null) {
            Log.e(logTag, "Assertion model name could not be established!")
            return false
        }

        // Capture the state
        val state = actionUtils.captureState(getInputSize(assertModel))

        // Run inference on the model
        val inference = inference(
            assertModel,
            state,
            enumClass.enumConstants?.map { it.name } ?: emptyList()
        )

        // Establish the results
        val inferenceResult = inference.predictions
            .filter { it.score >= inferenceLimit }
            .mapNotNull { prediction ->
                viewEntities.find {
                    it.name.equals(prediction.label, ignoreCase = true)
                }
            }

        Log.d(logTag, "Assertion predictions: ${inference.predictions}")

        // Establish the results
        val expectedEntities = viewEntities.joinToString(", ") { it.name }
        val inferredEntities = inferenceResult.joinToString(", ") { it.name }

        Log.d(logTag, "Expected view assertion results: $expectedEntities")
        Log.d(logTag, "Inferred view assertion results: $inferredEntities")

        // Check whether the assertion was successful
        val assert = viewEntities == inferenceResult

        if (assert) {
            Log.i(logTag, "View entities asserted successfully!")
        } else {
            Log.i(logTag, "View entities assertion failed!")
        }

        return assert
    }
}