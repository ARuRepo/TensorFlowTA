import os

import coremltools as ct
import math
import tensorflow as tf


class TensorflowModel(tf.Module):

    def __init__(self, configuration, log_message, refresh_application):
        super().__init__()
        self.configuration = configuration
        self.log_message = log_message
        self.refresh_application = refresh_application
        self.stop_training = False
        self.model = None

    # Method for creating the model
    def create_model(self, input_size, output_size, model_path, output_names):
        self.model = tf.keras.Sequential([
            tf.keras.layers.RandomZoom(height_factor=self.configuration.zoom_factor,
                                       width_factor=self.configuration.zoom_factor,
                                       input_shape=(input_size, input_size, self.configuration.num_channels)),
            tf.keras.layers.Rescaling(1. / 255),
            tf.keras.layers.Conv2D(16, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(output_size, activation='sigmoid', name="output")
        ])

        # Set the name for the model
        self.model.name = "TensorFoundry"

        # Print model summary
        self.model.summary()

        # Compile the model
        self.compile_model()

        # Starting loss for the model
        model_loss = float("inf")

        # Finally save the model
        self.save_model(model_path, model_loss, output_names)

    # Method for compiling the model
    def compile_model(self):
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                tf.keras.metrics.BinaryAccuracy(name='binary_accuracy'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ])

    # Method for training a supervised model
    def train_model(self, model_path, epochs, training_dataset, validation_dataset, class_names, plot_results):

        # Load a model and set as the current model
        self.model = tf.keras.models.load_model(model_path)
        self.log_message("Beginning training of model: {}".format(model_path))

        self.model.pop()
        self.model.add(tf.keras.layers.Dense(len(class_names), activation='sigmoid', name="output"))
        self.compile_model()

        # Read the minimum allowed loss in case of re-training
        model_loss = self.get_model_loss(model_path)

        # Train the model
        self.log_message("Starting the supervised training sequence with {} epochs!".format(epochs.get()))
        self.model.fit(training_dataset,
                       validation_data=validation_dataset,
                       epochs=epochs.get(),
                       callbacks=[TrainingCallback(
                           self.log_message,
                           self.refresh_application,
                           self.stop_training_check,
                           self.configuration.loss_improvement_limit,
                           self.configuration.loss_decay_rate,
                           self.configuration.bad_epoch_limit,
                           self.save_model,
                           plot_results,
                           model_path,
                           class_names,
                           model_loss)])

        # Evaluate the model which was saved last
        self.model = tf.keras.models.load_model(model_path)
        results = self.model.evaluate(validation_dataset, verbose=2, return_dict=True)
        self.log_message("Model validation results:")
        self.log_message(f"  Binary Accuracy: {results['binary_accuracy'] * 100:.2f}%")
        self.log_message(f"  Precision: {results['precision']:.4f}")
        self.log_message(f"  Recall: {results['recall']:.4f}")
        self.log_message(f"  Loss: {results['loss']:.4f}")

    # Method for returning the current status of the stop training to the callback
    def stop_training_check(self):
        return self.stop_training

    # Method for returning the input shape of a model
    def get_model_input(self, model_path):
        return tf.keras.models.load_model(model_path).input_shape[1:]

    # Method which reads the stored loss of the model from the model output file
    def get_model_loss(self, model_path):

        # Establish the file path
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        data_path = os.path.join(os.path.dirname(model_path), f"{model_name}_output.txt")

        # If the file does not exist we return maximum value loss
        if not os.path.isfile(data_path):
            return float("inf")

        with open(data_path, "r") as file:
            return float(file.readline().strip())

    # Method for testing the model
    def test_model(self, model_path, test_state, class_names):

        # Load a model and set as the current model
        self.model = tf.keras.models.load_model(model_path)
        predictions = self.model.predict(test_state)

        self.log_message("Predicted values:")
        for i, value in enumerate(predictions[0]):
            self.log_message(f"{class_names[i]}: {value:.4f}")

    # Method for saving the model
    def save_model(self, model_path, model_loss, output_names):

        model_name = os.path.splitext(os.path.basename(model_path))[0]

        # Writing the loss and output names into an output file
        labels_path = os.path.join(os.path.dirname(model_path), f"{model_name}_output.txt")

        with open(labels_path, 'w') as file:
            file.write(f"{model_loss}\n")
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
                 stop_training_check,
                 loss_improvement_limit,
                 loss_decay_rate,
                 bad_epoch_limit,
                 save_model,
                 plot_results,
                 model_path,
                 class_names,
                 min_loss):
        self.log_message = log_message
        self.refresh_application = refresh_application
        self.stop_training_check = stop_training_check
        self.loss_improvement_limit = loss_improvement_limit
        self.loss_decay_rate = loss_decay_rate
        self.bad_epoch_limit = bad_epoch_limit
        self.bad_epoch_count = 0
        self.save_model = save_model
        self.plot_results = plot_results
        self.model_path = model_path
        self.class_names = class_names
        self.min_loss = min_loss
        self.plot_accuracy = [0.0]
        self.plot_loss = [0.0]

    def on_epoch_end(self, epoch, logs=None):
        accuracy = logs.get("binary_accuracy", 0)
        loss = logs.get("val_loss", float('inf'))
        precision = logs.get("val_precision", 0)
        recall = logs.get("val_recall", 0)

        self.plot_accuracy.append(float("{:5.2f}".format(accuracy * 100)))
        self.plot_loss.append(float("{:5.4f}".format(loss)))
        self.plot_results(self.plot_accuracy, self.plot_loss)

        self.log_message(
            "Epoch {} - Binary Accuracy: {:5.2f}% | Precision: {:.4f} | Recall: {:.4f} | Loss: {:5.4f}".format(
                epoch,
                accuracy * 100,
                precision,
                recall,
                loss))

        # Collapse detection
        if precision == 0 and recall == 0:
            self.bad_epoch_count += 1
            self.log_message(f"Bad training epoch {epoch} current bad epoch count: {self.bad_epoch_count} "
                             f"out of {self.bad_epoch_limit}")
        else:
            self.bad_epoch_count = 0

        # Checking if we need to stop training
        if self.bad_epoch_count >= self.bad_epoch_limit or self.stop_training_check():
            self.log_message(f"Stopping model training at epoch {epoch}!")
            self.model.stop_training = True

        # Calculating a dynamic limit used to save the model
        dynamic_loss_limit = self.loss_improvement_limit * math.exp(-self.loss_decay_rate * epoch)

        # Save model if validation loss improves
        if loss < self.min_loss - dynamic_loss_limit and not self.model.stop_training:
            self.min_loss = loss
            self.save_model(self.model_path, self.min_loss, self.class_names)
            self.log_message(f"New best model saved at epoch {epoch} with loss {loss:.4f}")

    def on_train_batch_end(self, batch, logs=None):
        self.refresh_application()
