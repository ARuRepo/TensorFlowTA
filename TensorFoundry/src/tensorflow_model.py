import os
import tensorflow as tf
import coremltools as ct


class TensorflowModel(tf.Module):

    def __init__(self, configuration, log_message, refresh_application):
        super().__init__()
        self.configuration = configuration
        self.log_message = log_message
        self.refresh_application = refresh_application
        self.stop_training = False

    # Method for creating the model
    def create_model(self, input_size, output_size, model_path, output_names):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Rescaling(1. / 255, input_shape=(input_size, input_size, self.configuration.num_channels)),
            tf.keras.layers.Conv2D(16, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(output_size, activation='softmax', name="output")
        ])

        # Set the name for the model
        self.model.name = "SUPERVISED"

        # Print model summary
        self.model.summary()

        # Compile the model
        self.compile_model()

        # Finally save the model
        self.save_model(model_path, output_names)

    # Method for compiling the model
    def compile_model(self):
        self.model.compile(
            optimizer='adam',
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy'])

    # Method for training a supervised model
    def train_model(self, model_path, epochs, training_dataset, class_names, plot_results):

        # Load a model and set as the current model
        self.model = tf.keras.models.load_model(model_path)
        self.log_message("Beginning training of model: {}".format(model_path))

        self.model.pop()
        self.model.add(tf.keras.layers.Dense(len(class_names), activation='softmax', name="output"))
        self.compile_model()

        # Train the model
        self.log_message("Starting the supervised training sequence with {} epochs!".format(epochs.get()))
        self.model.fit(training_dataset,
                       validation_data=training_dataset,
                       epochs=epochs.get(),
                       callbacks=[TrainingCallback(
                           self.log_message, self.refresh_application, plot_results, self.stop_training_check)])

        loss, accuracy = self.model.evaluate(training_dataset, verbose=2)
        self.log_message("Model test dataset accuracy: {:5.2f}% and loss: {:5.4f}".format(100 * accuracy, loss))

        # Save the trained model
        self.save_model(model_path, class_names)

    # Method for returning the current status of the stop training to the callback
    def stop_training_check(self):
        return self.stop_training

    # Method for returning the input shape of a model
    def get_model_input(self, model_path):
        return tf.keras.models.load_model(model_path).input_shape[1:]

    # Method for testing the model
    def test_model(self, model_path, test_state, class_names):

        # Load a model and set as the current model
        self.model = tf.keras.models.load_model(model_path)
        predictions = self.model.predict(test_state)

        self.log_message("Predicted values:")
        for i, value in enumerate(predictions[0]):
            self.log_message(f"{class_names[i]}: {value:.4f}")

    # Method for saving the model
    def save_model(self, model_path, output_names):

        model_name = os.path.splitext(os.path.basename(model_path))[0]

        # Writing the output names into a file
        labels_path = os.path.join(os.path.dirname(model_path), f"{model_name}_output_labels.txt")

        with open(labels_path, 'w') as file:
            for output_name in output_names: file.write(output_name + "\n")

        # Sanity check needed on certain platforms
        if not model_path.lower().endswith(".keras"):
            model_path += ".keras"

        self.model.save(model_path)
        self.log_message("The .keras model saved at: {}".format(model_path))

    # Method for converting a model from .keras to .tflite
    def convert_model_tflite(self, path):

        # Load the model
        model = tf.keras.models.load_model(path)

        # Convert the model
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,  # enable LiteRT ops.
            tf.lite.OpsSet.SELECT_TF_OPS  # enable TensorFlow ops.
        ]
        tflite_model = converter.convert()

        # Save the model
        model_path = path.replace(".keras", ".tflite")
        with open(model_path, 'wb') as f:
            f.write(tflite_model)

        self.log_message("New TFlite model created at: {}".format(model_path))

    # Method for converting a model from .keras to .coreml
    def convert_model_coreml(self, path):

        # Load the model
        model = tf.keras.models.load_model(path)

        # Convert the model
        coreml_model = ct.convert(model=model, source="tensorflow")

        # Save the model
        model_path = path.replace(".keras", ".coreml")
        coreml_model.save(model_path)

        self.log_message("New CoreML model created at: {}".format(model_path))


class TrainingCallback(tf.keras.callbacks.Callback):

    def __init__(self,
                 log_message,
                 refresh_application,
                 plot_results,
                 stop_training_check):
        self.log_message = log_message
        self.refresh_application = refresh_application
        self.plot_results = plot_results
        self.stop_training_check = stop_training_check
        self.plot_accuracy = [0.0]
        self.plot_loss = [0.0]

    def on_epoch_end(self, epoch, logs=None):
        self.plot_accuracy.append(float("{:5.2f}".format(logs["accuracy"] * 100)))
        self.plot_loss.append(float("{:5.4f}".format(logs["loss"])))
        self.plot_results(self.plot_accuracy, self.plot_loss)

        self.log_message(
            "Epoch {} accuracy: {:5.2f}% loss: {:5.4f}".format(epoch, logs["accuracy"] * 100, logs["loss"]))

        # Checking if we need to stop training and save the model
        if self.stop_training_check():
            self.log_message("Stopping model training at epoch {}!".format(epoch))
            self.model.stop_training = True

    def on_train_batch_end(self, batch, logs=None):
        self.refresh_application()
