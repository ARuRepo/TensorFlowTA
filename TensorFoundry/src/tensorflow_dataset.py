import json
import os

import numpy as np
import tensorflow as tf


class DataSet:

    def __init__(self, configuration, log_message, plot_dataset, input_size):
        self.configuration = configuration
        self.log_message = log_message
        self.plot_dataset = plot_dataset
        self.input_size = input_size
        self.batch_size = 32

    # Method which creates the test datasets for supervised training
    def create_datasets(self, dataset_path, class_names):

        images_path = f"{dataset_path}/images"
        annotations_path = f"{dataset_path}/annotations.json"

        try:

            # Sanity check to make sure there is sufficient training data
            file_count = 0
            for _, _, files in os.walk(images_path):
                file_count += len(files)

            if file_count < self.configuration.min_dataset_size:
                self.log_message(f"Too few dataset files detected for training, needs contain at least "
                                 f"{self.configuration.min_dataset_size} files!")
                return None, None



            # Sanity check for the annotations file
            if not os.path.exists(annotations_path):
                self.log_message(f"Error reading the annotations file: {annotations_path}")
                return None, None

            # Load annotations from JSON file
            with open(annotations_path, 'r') as f:
                annotations = json.load(f)

            self.log_message(f"Loaded {len(annotations)} annotations from {annotations_path}")

            # Prepare lists for images and labels
            image_paths = []
            multi_labels = []

            for image_name, label_vector in annotations.items():
                image_path = os.path.join(images_path, image_name)

                # Check if image exists
                if not os.path.exists(image_path):
                    self.log_message(f"Warning: Image not found: {image_path}")
                    continue

                # Validate label vector length
                if len(label_vector) != len(class_names):
                    self.log_message(f"Label vector length mismatch for {image_name}. "
                                     f"Expected {len(class_names)}, got {len(label_vector)}")
                    continue

                # Only append if both checks passed
                image_paths.append(image_path)
                multi_labels.append(label_vector)

            if len(image_paths) < self.configuration.min_dataset_size:
                self.log_message("Too few valid dataset files detected for training, needs at least {} files!".format(
                    self.configuration.min_dataset_size))
                return None, None

            self.log_message(f"Found {len(image_paths)} valid images with annotations")

            # Convert to numpy arrays
            multi_labels = np.array(multi_labels, dtype=np.float32)

            # Helper function to load and preprocess images


            # Create dataset from image paths and labels
            dataset = tf.data.Dataset.from_tensor_slices((image_paths, multi_labels))
            dataset = dataset.map(lambda path, label: (self.load_image(path), label),
                                  num_parallel_calls=tf.data.AUTOTUNE)

            # Shuffle the dataset for training
            dataset = dataset.shuffle(buffer_size=min(len(image_paths), self.configuration.shuffle_buffer_size),
                                      seed=self.configuration.training_seed)

            # Split into training and validation
            train_size = int((1 - self.configuration.validation_split) * len(image_paths))

            training_dataset = dataset.take(train_size).batch(self.batch_size)
            validation_dataset = dataset.skip(train_size).batch(self.batch_size)

            # Add class_names attribute for compatibility
            training_dataset.class_names = class_names
            validation_dataset.class_names = class_names

            # Plotting the dataset preview
            self.plot_dataset(training_dataset)

            # Optimize datasets
            training_dataset = training_dataset.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
            validation_dataset = validation_dataset.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

            return training_dataset, validation_dataset

        except Exception as e:
            self.log_message(f"Error creating multi-label dataset: {e}")
            return None, None

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


    def load_image(self, image_path):
        image = tf.io.read_file(image_path)
        image = tf.image.decode_image(image, channels=self.configuration.num_channels, expand_animations=False)
        image = tf.image.resize(image, [self.input_size[0], self.input_size[1]])
        return image