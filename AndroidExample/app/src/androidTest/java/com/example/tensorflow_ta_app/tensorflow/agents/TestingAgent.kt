package com.example.tensorflow_ta_app.tensorflow.agents

import android.util.Log
import com.example.tensorflow_ta_app.utilities.ActionUtils
import com.example.tensorflow_ta_app.data.TestData
import com.example.tensorflow_ta_app.data.TestData.ActionData
import com.example.tensorflow_ta_app.data.TestData.AssertData
import com.example.tensorflow_ta_app.tensorflow.models.TestingModel
import org.tensorflow.lite.Interpreter

/**
 * This class is for calling the model specific classes to run inference and then handle the results
 */

class TestingAgent : TestingModel() {

    private val logTag = "TestingAgent"
    private val actionUtils = ActionUtils()
    private val taskModel: Interpreter = createModel("taskmodel.tflite")
    private val assertModel: Interpreter = createModel("assertmodel.tflite")
    private val taskLabels: List<String> = ActionData.entries.map { it.name }
    private val assertLabels: List<String> = AssertData.entries.map { it.name }
    private val taskInputSize: Int = getInputSize(taskModel)
    private val assertInputSize: Int = getInputSize(assertModel)

    private val taskComplete = ActionData.TASK_COMPLETE
    private val inferenceLimit = 0.9f
    private val actionsLimit = 10

    /**
     * Function which predicts an action using the task model
     * @param task the current task to execute
     * @param state the state which is to be validated to be either visible or not
     * @return Boolean value whether the task is completed and state is asserted to match expectation
     */
    fun performTaskAndAssert(task: TestData.TaskData, state: AssertData): Boolean {
        performTask(task)
        return assertState(state)
    }

    /**
     * Function which predicts an action using the task model
     * @param task the current task to execute
     * @return true or false if the task was completed successfully
     */
    fun performTask(task: TestData.TaskData) {

        val taskName = TestData.TaskData.entries[task.ordinal].name
        Log.i(logTag, "Starting to execute task $taskName")

        for (count in 0 until actionsLimit) {

            val state = actionUtils.captureState(taskInputSize, task.ordinal)

            // Figure out which action to carry out
            val inference = inference(taskModel, state, taskLabels)
            val maxScore = inference.predictions.maxByOrNull { it.score }

            // Get the action index based on prediction certainty
            val actionIndex = if (maxScore?.score!! >= inferenceLimit) {
                inference.predictions.indexOf(maxScore)
            } else {
                taskComplete.ordinal
            }

            // Get the action name
            val actionName = ActionData.entries[inference.predictions.indexOf(maxScore)]

            Log.d(logTag, "Predictions: ${inference.predictions}")
            Log.i(logTag, "Action to execute $actionName")

            // Check if this action index indicates the task is complete
            if (actionIndex == taskComplete.ordinal) {
                Log.i(logTag, "Task $taskName execution complete!")
                return
            }

            // Perform an action based on what the model suggests
            ActionData.entries[actionIndex].execute()
        }

        Log.i(logTag, "Ran out of actions executing task: $taskName")
        return
    }

    /**
     * Function which returns true or false based on whether the current State is asserted
     * @param expectedState the state  which is to be validated to be either visible or not
     * @return Boolean value whether the state is asserted to match expectation
     */
    fun assertState(expectedState: AssertData): Boolean {

        // Take a screenshot as the state
        val state = actionUtils.captureState(assertInputSize)

        // Figure out which state this is supposed to be
        val inference = inference(assertModel, state, assertLabels)
        val maxScore = inference.predictions.maxByOrNull { it.score }
        val stateIndex = inference.predictions.indexOf(maxScore)

        // Get the name of the current and expected states
        val currentName = AssertData.entries[stateIndex].name
        val expectedName = AssertData.entries[expectedState.ordinal].name

        Log.i(logTag, "State recognized as $currentName and expectation is $expectedName")

        // Evaluate if this is the view we are looking for
        return stateIndex == expectedState.ordinal
    }
}