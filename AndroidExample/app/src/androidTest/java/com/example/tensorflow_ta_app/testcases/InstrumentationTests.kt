package com.example.tensorflow_ta_app.testcases

import android.Manifest
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.rule.GrantPermissionRule
import com.example.tensorflow_ta_app.tensorflow.agents.TestingAgent
import com.example.tensorflow_ta_app.utilities.ActionUtils
import com.example.tensorflow_ta_app.data.TestData.TaskData.NAVIGATE_FIRST_SCREEN
import com.example.tensorflow_ta_app.data.TestData.TaskData.NAVIGATE_SECOND_SCREEN
import com.example.tensorflow_ta_app.data.TestData.TaskData.NAVIGATE_THIRD_SCREEN
import com.example.tensorflow_ta_app.data.TestData.AssertData.FIRST_SCREEN
import com.example.tensorflow_ta_app.data.TestData.AssertData.SECOND_SCREEN
import com.example.tensorflow_ta_app.data.TestData.AssertData.THIRD_SCREEN
import junit.framework.TestCase.assertTrue
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Navigation training tests used for on device training of the model, some syntax examples used
 */
@RunWith(AndroidJUnit4::class)
class InstrumentationTests {

    private val testingAgent = TestingAgent()
    private val actionUtils = ActionUtils()

    // NOTE: Run these with device frame disabled!

    @Rule
    @JvmField
    var grantPermissionRule: GrantPermissionRule = GrantPermissionRule.grant(
        Manifest.permission.READ_MEDIA_IMAGES,
        Manifest.permission.WRITE_EXTERNAL_STORAGE
    )

    /**
     * Setup function launches the application
     */
    @Before
    fun setUp() {
        actionUtils.launchApplication("com.example.tensorflow_ta_app")
    }

    /**
     * Teardown function which resets the app
     */
    @After
    fun tearDown() {
        actionUtils.performReset()
    }

    /**
     * Test which navigates to the first screen and asserts it
     */
    @Test
    fun loginNavigateAssertFirstScreen() {
        assertTrue(testingAgent.performTaskAndAssert(NAVIGATE_FIRST_SCREEN, FIRST_SCREEN))
    }

    /**
     * Test which navigates to the second screen and asserts it
     */
    @Test
    fun loginNavigateAssertSecondScreen() {
        with(testingAgent){
            assertTrue(performTaskAndAssert(NAVIGATE_SECOND_SCREEN, SECOND_SCREEN))
        }
    }

    /**
     * Test which navigates to the third screen and asserts it
     */
    @Test
    fun loginNavigateAssertThirdScreen() {
        with(testingAgent){
            performTask(NAVIGATE_THIRD_SCREEN)
            assertTrue(assertState(THIRD_SCREEN))
        }
    }
}