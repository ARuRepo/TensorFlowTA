package com.example.tensorflow_ta_app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.CutCornerShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.testTagsAsResourceId
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.tensorflow_ta_app.ui.theme.TensorFlow_TA_AppTheme

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalComposeUiApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TensorFlow_TA_AppTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier
                        .fillMaxSize()
                        .semantics {
                            testTagsAsResourceId = true
                        },
                    color = Color.Gray
                ) {
                    MainView()
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        println("onStart called")
    }

    override fun onResume() {
        super.onResume()
        println("onResume called")
    }

    override fun onPause() {
        super.onPause()
        println("onPause called")
    }

    override fun onStop() {
        super.onStop()
        println("onStop called")
    }

    override fun onDestroy() {
        super.onDestroy()
        println("onDestroy called")
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        println("onSaveInstanceState called")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        println("onRestoreInstanceState called")
    }
}

sealed class View(val route: String) {
    data object Login : View("login")
    data object View1 : View("view1")
    data object View2 : View("view2")
    data object View3 : View("view3")
}

class userName {
    var userName: String by mutableStateOf("")
}

class password {
    var password: String by mutableStateOf("")
}

@Composable
fun MainView() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = View.Login.route) {
        composable(View.Login.route) { LoginView(navController) }
        composable(View.View1.route) { FirstView(navController) }
        composable(View.View2.route) { SecondView(navController) }
        composable(View.View3.route) { ThirdView(navController) }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun LoginView(navController: NavController) {

    var userName = remember { userName() }
    var password = remember { password() }

    fun validCredentials(): Boolean {
        return userName.userName == "username" && password.password == "password"
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = ("Login View"),
            color = Color.White,
            style = MaterialTheme.typography.displayMedium,
            modifier = Modifier
                .testTag("login_view_title")
                .semantics { testTagsAsResourceId = true }
        )

        Spacer(modifier = Modifier.height(16.dp))

        UserNameTextField(userName)

        Spacer(modifier = Modifier.height(16.dp))

        PasswordTextField(password)

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {

                if (validCredentials()) {
                    navController.navigate(View.View1.route)
                } else {
                    navController.navigate(View.Login.route)
                }
            },
            colors = ButtonDefaults.buttonColors(Color.Blue),
            shape = RectangleShape,
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("login_view_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Login")
        }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun UserNameTextField(
    userName: userName = remember { userName() }
) {

    OutlinedTextField(
        value = userName.userName,
        onValueChange = { userName.userName = it },
        label = { Text("Username") },
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = Color.White,
            unfocusedContainerColor = Color.White,
            disabledContainerColor = Color.White,
            focusedLabelColor = Color.LightGray,
            unfocusedLabelColor = Color.LightGray,
            disabledLabelColor = Color.LightGray
        ),
        modifier = Modifier
            .testTag("login_view_username")
            .semantics { testTagsAsResourceId = true }
    )
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun PasswordTextField(
    password: password = remember { password() }
) {

    OutlinedTextField(
        value = password.password,
        onValueChange = { password.password = it },
        label = { Text("Password") },
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = Color.White,
            unfocusedContainerColor = Color.White,
            disabledContainerColor = Color.White,
            focusedLabelColor = Color.LightGray,
            unfocusedLabelColor = Color.LightGray,
            disabledLabelColor = Color.LightGray
        ),
        modifier = Modifier
            .testTag("login_view_password")
            .semantics { testTagsAsResourceId = true }
    )
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun FirstView(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = ("View One"),
            color = Color.White,
            style = MaterialTheme.typography.displayMedium,
            modifier = Modifier
                .testTag("first_view_title")
                .semantics { testTagsAsResourceId = true }
        )

        Spacer(modifier = Modifier.height(16.dp))

        Shape(
            shape = RectangleShape,
            color = Color.Blue,
            testTag = "first_view_shape"
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View2.route) },
            colors = ButtonDefaults.buttonColors(Color.Red),
            shape = RectangleShape,
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("first_view_next_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Next")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View3.route) },
            colors = ButtonDefaults.buttonColors(Color.Green),
            shape = CutCornerShape(10),
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("first_view_back_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Back")
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = { navController.navigate(View.Login.route) },
            colors = ButtonDefaults.buttonColors(Color.DarkGray),
            shape = CutCornerShape(10),
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("first_view_logout_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Logout")
        }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun SecondView(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = ("View Two"),
            color = Color.White,
            style = MaterialTheme.typography.displayMedium,
            modifier = Modifier
                .testTag("second_view_title")
                .semantics { testTagsAsResourceId = true }
        )

        Spacer(modifier = Modifier.height(16.dp))

        Shape(
            shape = CircleShape,
            color = Color.Green,
            testTag = "second_view_shape"
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View3.route) },
            colors = ButtonDefaults.buttonColors(Color.Blue),
            shape = CircleShape,
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("second_view_next_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Next")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View1.route) },
            colors = ButtonDefaults.buttonColors(Color.Red),
            shape = RectangleShape,
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("second_view_back_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Back")
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = { navController.navigate(View.Login.route) },
            colors = ButtonDefaults.buttonColors(Color.DarkGray),
            shape = CutCornerShape(10),
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("second_view_logout_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Logout")
        }
    }
}


@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun ThirdView(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {

        Text(
            text = ("View Three"),
            color = Color.White,
            style = MaterialTheme.typography.displayMedium,
            modifier = Modifier
                .testTag("third_view_title")
                .semantics { testTagsAsResourceId = true }
        )

        Spacer(modifier = Modifier.height(16.dp))

        Shape(
            shape = RoundedCornerShape(20.dp),
            color = Color.Red,
            testTag = "third_view_shape"
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View1.route) },
            colors = ButtonDefaults.buttonColors(Color.Green),
            shape = CutCornerShape(10),
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("third_view_next_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Next")
        }

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { navController.navigate(View.View2.route) },
            colors = ButtonDefaults.buttonColors(Color.Blue),
            shape = CircleShape,
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("third_view_back_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Back")
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = { navController.navigate(View.Login.route) },
            colors = ButtonDefaults.buttonColors(Color.DarkGray),
            shape = CutCornerShape(10),
            modifier = Modifier
                .padding(horizontal = 16.dp, vertical = 8.dp)
                .testTag("third_view_logout_button")
                .semantics { testTagsAsResourceId = true }
        ) {
            Text("Logout")
        }
    }
}

@OptIn(ExperimentalComposeUiApi::class)
@Composable
fun Shape(shape: Shape, color: Color, testTag: String) {
    Box(modifier = Modifier
        .height(100.dp)
        .width(100.dp)
        .clip(shape)
        .background(color)
        .testTag(testTag)
        .semantics { testTagsAsResourceId = true })
}

@Preview(showBackground = true)
@Composable
fun MainViewPreview() {
    TensorFlow_TA_AppTheme {
        MainView()
    }
}