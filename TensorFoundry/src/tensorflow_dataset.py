import os

import tensorflow as tf
from tensorflow.python.data import AUTOTUNE


class DataSet:

    def __init__(self, configuration, log_message, plot_dataset, input_size):
        self.configuration = configuration
        self.log_message = log_message
        self.plot_dataset = plot_dataset
        self.input_size = input_size
        self.batch_size = 32

    # Method which creates the test datasets for supervised training
    def create_datasets(self, path, class_names):

        # Sanity check to make sure there is sufficient training data
        file_count = 0
        for _, _, files in os.walk(path):
            file_count += len(files)

        if file_count < self.configuration.min_dataset_size:
            self.log_message("Too few dataset files detected for training, needs contain at least {} -files!".format(
                self.configuration.min_dataset_size))
            return None

        # Create the training dataset
        try:
            training_dataset = tf.keras.utils.image_dataset_from_directory(
                path,
                image_size=(self.input_size[0], self.input_size[1]),
                batch_size=self.batch_size,
                class_names=class_names
            )
        except:
            self.log_message("Error creating dataset, please check model and dataset output compatibility!")
            return None

        # Plotting the dataset
        self.plot_dataset(training_dataset)

        # Optimizing the datasets for training
        training_dataset = training_dataset.cache().prefetch(buffer_size=AUTOTUNE)

        return training_dataset

    # Method which loads a single image and labels to test a model's output
    def create_test_data(self, model_name, model_path, image_path):

        # Load the image and format it into a state for model input
        image = tf.keras.utils.load_img(image_path,
                                        target_size=(self.input_size[0], self.input_size[1], self.input_size[2]))
        test_state = tf.keras.utils.img_to_array(image)
        test_state = tf.expand_dims(test_state, 0)  # Create batch axis

        # Path to the file where the class names are saved
        labels_path = os.path.join(os.path.dirname(model_path), f"{model_name}_output_labels.txt")

        # Read the class names from the file into a list
        with open(labels_path, 'r') as file:
            class_names = [line.strip() for line in file]

        return test_state, class_names
