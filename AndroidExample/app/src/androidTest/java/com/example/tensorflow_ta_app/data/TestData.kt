package com.example.tensorflow_ta_app.data

import com.example.tensorflow_ta_app.utilities.ActionUtils

/**
 * This class is for holding any data needed for the testing
 */
class TestData {

    /**
     * Enum for the tasks
     */
    enum class NavigationData {
        PERFORM_LOGIN,
        PERFORM_LOGOUT,
        NAVIGATE_FIRST_SCREEN,
        NAVIGATE_SECOND_SCREEN,
        NAVIGATE_THIRD_SCREEN
    }

    /**
     * Enum for the assertions in the login view
     */
    enum class LoginViewAssertData {
        LOGIN_TITLE,
        USER_NAME_FIELD,
        PASSWORD_FIELD,
        LOGIN_BUTTON
    }

    /**
     * Enum for the assertions in the first view
     */
    enum class FirstViewAssertData {
        VIEW_TITLE,
        SQUARE_SHAPE,
        NEXT_BUTTON,
        BACK_BUTTON,
        LOGOUT_BUTTON
    }

    /**
     * Enum for the assertions in the second view
     */
    enum class SecondViewAssertData {
        VIEW_TITLE,
        CIRCLE_SHAPE,
        NEXT_BUTTON,
        BACK_BUTTON,
        LOGOUT_BUTTON
    }

    /**
     * Enum for the assertions in the third view
     */
    enum class ThirdViewAssertData {
        VIEW_TITLE,
        SQUIRCLE_SHAPE,
        NEXT_BUTTON,
        BACK_BUTTON,
        LOGOUT_BUTTON
    }

    /**
     * Enum for the action functions
     */
    enum class ActionData {
        STAND_BY {
            override fun execute(): Any {
                return actions.standBy()
            }
        },
        SWIPE_UP {
            override fun execute(): Any {
                return actions.swipe(SWIPE_UP)
            }
        },
        SWIPE_DOWN {
            override fun execute(): Any {
                return actions.swipe(SWIPE_DOWN)
            }
        },
        PERFORM_LOGIN {
            override fun execute(): Any {
                return actions.performLogin()
            }
        },
        PERFORM_LOGOUT {
            override fun execute(): Any {
                return actions.tapButton(ButtonData.LOGOUT_BUTTON)
            }
        },
        TAP_NEXT_BUTTON {
            override fun execute(): Any {
                return actions.tapButton(ButtonData.NEXT_BUTTON)
            }
        },
        TAP_BACK_BUTTON {
            override fun execute(): Any {
                return actions.tapButton(ButtonData.BACK_BUTTON)
            }
        },
        TASK_COMPLETE {
            override fun execute(): Any {
                return actions.standBy()
            }
        };

        abstract fun execute(): Any

        companion object {
            val actions = ActionUtils()
        }
    }

    /**
     * Enum for the login credentials
     */
    enum class TextData(val value: String) {
        USERNAME_TEXT("username"),
        PASSWORD_TEXT("password"),
    }

    /**
     * Enum for the buttons
     */
    enum class ButtonData(val value: String) {
        LOGIN_BUTTON("Login"),
        LOGOUT_BUTTON("Logout"),
        NEXT_BUTTON("Next"),
        BACK_BUTTON("Back"),
    }
}