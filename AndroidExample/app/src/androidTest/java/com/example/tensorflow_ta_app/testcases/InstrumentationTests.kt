package com.example.tensorflow_ta_app.testcases

import android.Manifest
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.rule.GrantPermissionRule
import com.example.tensorflow_ta_app.data.TestData.LoginViewAssertData
import com.example.tensorflow_ta_app.data.TestData.FirstViewAssertData
import com.example.tensorflow_ta_app.data.TestData.SecondViewAssertData
import com.example.tensorflow_ta_app.data.TestData.ThirdViewAssertData
import com.example.tensorflow_ta_app.data.TestData.NavigationData.NAVIGATE_FIRST_SCREEN
import com.example.tensorflow_ta_app.data.TestData.NavigationData.NAVIGATE_SECOND_SCREEN
import com.example.tensorflow_ta_app.data.TestData.NavigationData.NAVIGATE_THIRD_SCREEN
import com.example.tensorflow_ta_app.tensorflow.agents.TestingAgent
import com.example.tensorflow_ta_app.utilities.ActionUtils
import junit.framework.TestCase.assertTrue
import org.junit.After
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Some basic test cases using the ML model to navigate and assert the views
 */
@RunWith(AndroidJUnit4::class)
class InstrumentationTests {

    private val testingAgent = TestingAgent()
    private val actionUtils = ActionUtils()

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
     * Test which asserts the login view contents
     */
    @Test
    fun assertLoginView() {

        val viewEntities = listOf(
            LoginViewAssertData.LOGIN_TITLE,
            LoginViewAssertData.USER_NAME_FIELD,
            LoginViewAssertData.PASSWORD_FIELD,
            LoginViewAssertData.LOGIN_BUTTON
        )

        with(testingAgent) {
            assertTrue(assertViewEntities(viewEntities))
        }
    }

    /**
     * Test which navigates to the first view and asserts the contents
     */
    @Test
    fun loginNavigateAssertFirstView() {

        val viewEntities = listOf(
            FirstViewAssertData.VIEW_TITLE,
            FirstViewAssertData.SQUARE_SHAPE,
            FirstViewAssertData.NEXT_BUTTON,
            FirstViewAssertData.BACK_BUTTON,
            FirstViewAssertData.LOGOUT_BUTTON
        )

        assertTrue(testingAgent.navigateAndAssert(NAVIGATE_FIRST_SCREEN, viewEntities))
    }

    /**
     * Test which navigates to the second view and asserts the contents
     */
    @Test
    fun loginNavigateAssertSecondView() {

        val viewEntities = listOf(
            SecondViewAssertData.VIEW_TITLE,
            SecondViewAssertData.CIRCLE_SHAPE,
            SecondViewAssertData.NEXT_BUTTON,
            SecondViewAssertData.BACK_BUTTON,
            SecondViewAssertData.LOGOUT_BUTTON
        )

        with(testingAgent) {
            assertTrue(navigateAndAssert(NAVIGATE_SECOND_SCREEN, viewEntities))
        }
    }

    /**
     * Test which navigates to the third view and asserts the contents
     */
    @Test
    fun loginNavigateAssertThirdView() {

        val viewEntities = listOf(
            ThirdViewAssertData.VIEW_TITLE,
            ThirdViewAssertData.SQUIRCLE_SHAPE,
            ThirdViewAssertData.NEXT_BUTTON,
            ThirdViewAssertData.BACK_BUTTON,
            ThirdViewAssertData.LOGOUT_BUTTON
        )

        with(testingAgent) {
            performNavigation(NAVIGATE_THIRD_SCREEN)
            assertTrue(assertViewEntities(viewEntities))
        }
    }
}