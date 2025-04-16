import os
import platform
from tkinter import END, messagebox, ttk, Listbox

from PIL import Image
from PIL.Image import Resampling
from matplotlib import image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from application_utils import DialogType, read_output_labels, read_task_labels, filepath_dialog
from src.input_dialog import InputDialog


class CreateDataset:
    def __init__(self, app, configuration, log_message, tensorflow_model):
        self.app = app
        self.configuration = configuration
        self.log_message = log_message
        self.tensorflow_model = tensorflow_model
        self.dataset_log_listbox = None
        self.task_listbox = None
        self.link_output_listbox = None
        self.source_images_path = None
        self.source_entries = None
        self.source_plot_figure = None
        self.source_plot_canvas = None
        self.source_plot = None
        self.dataset_folder = None
        self.dataset_link_actions = []
        self.dataset_input_size = None

    # Method which logs into the dataset log listbox
    def print_dataset_log(self, messages):
        for msg in messages:
            self.dataset_log_listbox.insert(END, msg)
            self.dataset_log_listbox.yview(END)

        if self.dataset_log_listbox.index("end") > self.configuration.log_limit:
            self.dataset_log_listbox.delete(0)

    def disable_log_selection(self, event):
        self.dataset_log_listbox.selection_clear(0, END)

    # Method which updates the current image when task selection changes
    def select_listbox_task(self, event):

        if self.source_entries:
            task_index = self.task_listbox.curselection()

            # Display an image based on whether a task exists
            if task_index:
                self.plot_source(self.source_entries[task_index[0]][0],
                                 self.source_entries[task_index[0]][1][0])
            else:
                self.plot_source(self.source_entries[0][0], self.source_entries[0][1][0])

    # Method for handling the import task button
    def import_task_button(self):

        self.log_message("Please select a task labels file")
        tasks_path, load_tasks = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a task labels file:",
            [('Tasks file', '.txt')])

        if load_tasks:
            with open(tasks_path, "r") as file:
                lines = [label.strip() for label in file.readlines()]
                self.task_listbox.delete(0, END)
                for line in lines:
                    self.task_listbox.insert(END, line.strip())

    # Method for handling the add task button
    def add_task_button(self):

        # Asking for a task name and checking if it already exists
        self.log_message("Please enter dataset task name")
        task_name = InputDialog(self.app,
                                self.configuration, "Task name", "Enter dataset task name:").result

        if task_name:
            task_name = task_name.upper()
            if task_name in self.task_listbox.get(0, END):
                self.log_message("Task {} already exists!".format(task_name))
                return

            self.task_listbox.insert(END, task_name)
            self.task_listbox.yview(END)

            if self.dataset_folder:
                self.create_source_entries()

            if self.task_listbox.size() == 1:
                self.task_listbox.select_set(0)

            self.select_listbox_task(self)

        return

    # Method for handling the remove task button
    def remove_task_button(self):
        task_index = self.task_listbox.curselection()
        if task_index:

            if self.dataset_folder:
                self.remove_source_entries(task_index[0])

            self.task_listbox.delete(task_index)
            self.task_listbox.select_set(task_index[0] - 1 if task_index[0] > 0 else 0)

            # Remove any dataset link actions matching this task
            self.dataset_link_actions = [
                index for index in self.dataset_link_actions
                if index[0] != task_index[0]
            ]

            if self.task_listbox.size() == 0:
                self.create_source_entries()

        self.select_listbox_task(self)

        return

    # Method which creates a folder for each specified output
    def create_dataset_folders(self, dataset_path, dataset_name, output_labels):

        self.dataset_folder = os.path.join(dataset_path, dataset_name)
        os.makedirs(self.dataset_folder, exist_ok=True)

        output_folders = [output.strip() for output in output_labels]

        for folder in output_folders:
            folder_path = os.path.join(str(self.dataset_folder), folder)
            os.makedirs(folder_path, exist_ok=True)

        self.log_message("Created dataset structure at: {}".format(self.dataset_folder))
        return

    # Method for reading image files from a target folder
    def find_image_filepaths(self, images_path):

        image_types = [".jpg", ".jpeg", ".png", ".gif"]
        image_paths = []

        # Read all compatible image files from the target folder
        for root, dirs, files in os.walk(images_path):
            for image in files:
                if any(image.lower().endswith(type) for type in image_types):
                    image_paths.append(os.path.join(root, image))

        return image_paths

    # Method which filters out image filepaths which already exists in the dataset
    def filter_source_images(self, source_images, task_name):

        images_list = []

        # Check if the task augmented image exists in the target dataset
        for source_image in source_images:

            image_name, image_extension = os.path.splitext(os.path.basename(source_image))

            if task_name:
                image_name += f"_{task_name}"

            image_name += image_extension

            # Searching if the current image is not included in any existing images in the dataset
            found = False
            for root, dirs, files in os.walk(self.dataset_folder):

                # Filter to only include .png files
                png_files = [file for file in files if file.endswith('.png')]

                if image_name in png_files:
                    found = True
                    break

            if not found:
                images_list.append(source_image)

        return images_list

    # Method which converts and saves it to target folder
    def save_image(self, image_path, save_path):
        with Image.open(image_path) as image:
            # Crop the top bar off the image
            width, height = image.size
            image = image.crop((0, int(height * 0.05), width, height))

            # Resize and format the image
            image = image.resize(
                [self.dataset_input_size[0], self.dataset_input_size[1]],
                resample=Resampling.NEAREST
            )

            # Convert to RGB and save the image
            image = image.convert('RGB')
            image.save(save_path, format='PNG')

    # Method for deleting a dataset image
    def delete_image(self, image_path):
        try:
            os.remove(image_path)
            self.log_message(f"{image_path} has been deleted.")
        except FileNotFoundError:
            self.log_message(f"{image_path} does not exist!")
        except PermissionError:
            self.log_message(f"You don't have permission to delete {image_path}!")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Method for adding a task to an output
    def link_output_button(self):

        # Sanity check in case no source entries were found
        if self.source_entries is None:
            return

        # Try to get the currently selected task
        task_index = self.task_listbox.curselection()
        task_name = None
        source_entry_index = 0

        # Determine the current source entry index based on any selected task
        if task_index:
            task_name = self.task_listbox.get(task_index)
            source_entry_index = self.get_source_entry_index(task_name)

        # Sanity check in case all images have been added to dataset
        if len(self.source_entries[source_entry_index][1]) == 0:
            return

        # Output index
        link_output_index = self.link_output_listbox.curselection()

        if not link_output_index:
            self.log_message("No dataset output selected!")
            return

        link_output_name = self.link_output_listbox.get(link_output_index)

        # Update the image name if task is selected
        source_image_name = os.path.basename(self.source_entries[source_entry_index][1][0])

        if task_index:
            source_image_name = (
                    os.path.splitext(source_image_name)[0] + "_" + task_name + ".png")

        dataset_image_path = os.path.join(self.dataset_folder, link_output_name, source_image_name)

        # Save the image to the destination dataset folder as bitmap
        self.save_image(self.source_entries[source_entry_index][1][0], dataset_image_path)

        # Augment the image with the task index if available so it can be recognized
        if task_index:
            self.augment_image_task(dataset_image_path, task_index[0])

        self.log_message("Added image: {} into dataset output: '{}'".format(source_image_name, link_output_name))

        source_task_name = self.source_entries[source_entry_index][0]
        source_image_path = self.source_entries[source_entry_index][1][0]

        # Add into the list of completed actions
        self.dataset_link_actions.insert(0,
                                         (
                                             source_entry_index,
                                             source_task_name,
                                             source_image_path,
                                             dataset_image_path
                                         )
                                         )

        # Remove the image from the current task source entry
        self.source_entries[source_entry_index][1].pop(0)

        # Sanity check in case all images have been added to dataset
        if len(self.source_entries[source_entry_index][1]) == 0:
            self.log_message("All images for this configuration have been added into the dataset!")
            self.clear_source()
            return

        # Update for drawing the correct image
        source_task_name = self.source_entries[source_entry_index][0]
        source_image_path = self.source_entries[source_entry_index][1][0]

        # Display the next image
        self.plot_source(source_task_name, source_image_path)

    # Method for undoing a linking which was just done
    def undo_linking_button(self):

        # Sanity check to see if there are any recorded actions
        if len(self.dataset_link_actions) == 0:
            return

        # Delete existing image from dataset
        self.delete_image(self.dataset_link_actions[0][3])

        # Get the source entry index
        source_entry_index = self.dataset_link_actions[0][0]

        # Add the image back into the source entries
        self.source_entries[source_entry_index][1].insert(0, self.dataset_link_actions[0][2])

        # Retrieve the source task and image paths
        source_task_name = self.dataset_link_actions[0][1]
        source_image_path = self.dataset_link_actions[0][2]

        # Display the returned image
        self.plot_source(source_task_name, source_image_path)

        # Finally remove the link action as it has been undone
        self.dataset_link_actions.pop(0)

        return

    # Method which determine the current source entry index based on any selected task
    def get_source_entry_index(self, task_name):
        source_entry_index = (
            next((i for i, source_entry in enumerate(self.source_entries) if task_name in source_entry), 0))

        return source_entry_index

    # Method which adds the task value to the pixels of an image
    def augment_image_task(self, image_path, task_index):

        # Open the image
        with Image.open(image_path) as image:

            if image.mode != 'RGB':
                self.log_message("Image must be an RGB bitmap to augment!")
                return

            # Get the image dimensions
            width, height = image.size
            prev_red, prev_green, prev_blue = 0, 0, 0
            augmented_red, augmented_green, augmented_blue = 0, 0, 0

            # Iterate through each pixel and modify its values
            pixels = image.load()
            for x in range(width):
                for y in range(height):
                    pixel_red, pixel_green, pixel_blue = pixels[x, y]

                    # If matching, update the pixel value using the previous values
                    if pixel_red == prev_red and pixel_green == prev_green and pixel_blue == prev_blue:
                        pixels[x, y] = (augmented_red, augmented_green, augmented_blue)

                    else:
                        # Add or subtract the value from each color channel
                        augmented_red = self.augment_pixel(pixel_red + task_index)
                        augmented_green = self.augment_pixel(pixel_green + task_index)
                        augmented_blue = self.augment_pixel(pixel_blue + task_index)

                        # Update the pixel value
                        pixels[x, y] = (augmented_red, augmented_green, augmented_blue)

                    prev_red = pixel_red
                    prev_green = pixel_green
                    prev_blue = pixel_blue

            self.log_message("Image was augmented with task: {}".format(self.task_listbox.get(task_index)))

            # Save the modified image
            image.save(image_path)
            return

    # Method for handling the create dataset button
    def create_dataset_button(self):
        self.create_load_dataset(new_dataset=True)

    # Method for handling the load dataset button
    def load_dataset_button(self):
        self.create_load_dataset(new_dataset=False)

    # Method for handling the create and load dataset button
    def create_load_dataset(self, new_dataset):

        self.log_message("Please select a model")
        model_path, load_model = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a model:",
            [('Keras models', '.keras')])

        if not load_model:
            return

        model_name = os.path.splitext(os.path.basename(model_path))[0]

        # Read the output labels and populate the actions listbox
        output_labels, load_outputs = read_output_labels(model_name, model_path)

        if not load_outputs:
            self.log_message("Could not read the {}_output_labels.txt as actions!".format(model_name))
            return

        # Store the input size of the model
        self.dataset_input_size = self.tensorflow_model.get_model_input(model_path)

        # Ask where to find the source images
        self.log_message("Please select the source images directory")
        self.source_images_path, images_found = (
            filepath_dialog(self.app, DialogType.SELECTDIR, "Please select the source images directory:"))

        if not images_found:
            return

        dataset_name = ""

        if new_dataset:

            self.log_message("Please enter dataset name")
            dataset_name = InputDialog(self.app,
                                       self.configuration, "Dataset name", "Enter dataset name:").result

            if not dataset_name or dataset_name == "":
                return

            # Ask where to create the new dataset
            self.log_message("Please select where to create the dataset")
            self.dataset_folder, create_dataset = (
                filepath_dialog(self.app, DialogType.SELECTDIR, "Please select where to create the dataset:"))

            if not create_dataset:
                return

        else:

            # Ask where to load the dataset from
            self.log_message("Please select a dataset directory")
            self.dataset_folder, load_dataset = (
                filepath_dialog(self.app, DialogType.SELECTDIR, "Please select a dataset directory:"))

            if not load_dataset:
                return

            # Read the task labels and populate the tasks listbox
            task_labels, load_tasks = read_task_labels(self.dataset_folder)

            # Populate the tasks listbox
            self.task_listbox.delete(0, END)

            if load_tasks:
                for task_label in task_labels:
                    self.task_listbox.insert(END, task_label.strip())

        # Populate the output listbox
        self.link_output_listbox.delete(0, END)

        for output_label in output_labels:
            self.link_output_listbox.insert(END, output_label.strip())

        if new_dataset:
            # Create the folder structure
            self.create_dataset_folders(self.dataset_folder, dataset_name, output_labels)

        # Add dataset tasks
        self.create_source_entries()

        # Clear the link actions list
        self.dataset_link_actions.clear()

        # Set the tasks listbox selection to the first entry if there are entries
        if len(self.task_listbox.get(0, END)) > 0:
            self.task_listbox.select_set(0)

        # Display the first image to begin the dataset creation
        if self.source_entries:
            self.plot_source(self.source_entries[0][0], self.source_entries[0][1][0])

    # Method which creates source entries
    def create_source_entries(self):

        # List the source images
        source_images = self.find_image_filepaths(self.source_images_path)

        # List the tasks from the tasks listbox
        task_names = self.task_listbox.get(0, END)

        # If there are no tasks listed then adding a default empty one, otherwise creating the full set for each task
        if len(task_names) == 0:
            self.source_entries = [("",
                                    self.filter_source_images(source_images, ""))]
        else:
            self.source_entries = [(task,
                                    self.filter_source_images(source_images, task)) for
                                   task in task_names]

            # Writing the tasks into a file
            self.create_tasks_file()

        # If no new images were found then setting back to None
        if len(self.source_entries[0][1]) == 0:
            self.log_message("Could not find any new images from: {}".format(self.source_images_path))
            self.source_entries = None
            return

        self.log_message("Source images loaded from: {}".format(self.source_images_path))

        return

    # Method which removes task source entries
    def remove_source_entries(self, task_index):

        task_name = self.task_listbox.get(task_index)

        # Ask if user wants to remove any images with the task name
        if messagebox.askyesno("Remove data?", "Do you want to remove the task images from dataset?"):
            for root, dirs, files in os.walk(self.dataset_folder):
                for filename in files:
                    if task_name in filename:
                        os.remove(os.path.join(root, filename))

        # Remove the source entry matching the task index
        self.source_entries.pop(task_index)

        # Set the selection to the previous entry if it exists
        if len(self.task_listbox.get(0, END)) > 0:
            self.task_listbox.select_set(task_index - 1)

        return

    # Method which writes the current tasks into the dataset folder
    def create_tasks_file(self):

        if self.dataset_folder:

            task_names = self.task_listbox.get(0, END)
            tasks_path = os.path.join(self.dataset_folder, "dataset_tasks.txt")

            if len(task_names) > 0:
                with open(tasks_path, 'w') as file:
                    for task_name in task_names: file.write(task_name + "\n")

    # Linear Congruential Generator which generates a pseudo random value for a pixel
    def augment_pixel(self, seed):
        a = 1664525
        c = 1013904223
        m = 2 ** 32
        return ((a * seed + c) % m) % 256

    # Method which plots the source image
    def plot_source(self, task_name, image_path):
        self.source_plot_figure.clear()
        self.source_plot = self.source_plot_figure.add_subplot(1, 1, 1)
        self.source_plot.imshow(mpimg.imread(image_path))
        self.source_plot.set_title(task_name, fontsize=20, color=self.configuration.app_text_foreground_color)
        self.source_plot.axis("off")
        self.source_plot_canvas.draw()

    # Method which plots the source image
    def clear_source(self):
        self.source_plot_figure.clear()
        self.source_plot_canvas.draw()

    # Method which creates the UI for the Create Dataset tab
    def create_dataset_ui(self, create_dataset_tab):

        # Labels
        tasks_label = ttk.Label(
            create_dataset_tab,
            text="Dataset tasks:"
        )

        link_output_label = ttk.Label(
            create_dataset_tab,
            text="Model outputs:"
        )

        # Buttons
        import_task_button = ttk.Button(
            create_dataset_tab,
            text="Import",
            command=self.import_task_button,
            width=self.configuration.app_button_size
        )

        add_task_button = ttk.Button(
            create_dataset_tab,
            text="+",
            command=self.add_task_button,
            width=self.configuration.app_button_size
        )

        remove_task_button = ttk.Button(
            create_dataset_tab,
            text="-",
            command=self.remove_task_button,
            width=self.configuration.app_button_size
        )

        link_output_button = ttk.Button(
            create_dataset_tab,
            text="Link output",
            command=self.link_output_button,
            width=self.configuration.app_button_size
        )

        undo_linking_button = ttk.Button(
            create_dataset_tab,
            text="Undo linking",
            command=self.undo_linking_button,
            width=self.configuration.app_button_size
        )

        create_dataset_button = ttk.Button(
            create_dataset_tab,
            text="Create dataset",
            command=self.create_dataset_button,
            width=self.configuration.app_button_size
        )

        load_dataset_button = ttk.Button(
            create_dataset_tab,
            text="Load dataset",
            command=self.load_dataset_button,
            width=self.configuration.app_button_size
        )

        # List boxes
        self.dataset_log_listbox = Listbox(
            create_dataset_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            takefocus=0
        )

        self.dataset_log_listbox.bind("<<ListboxSelect>>", self.disable_log_selection)

        self.task_listbox = Listbox(
            create_dataset_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            width=self.configuration.app_listbox_size,
            exportselection=False
        )

        self.task_listbox.bind("<<ListboxSelect>>", self.select_listbox_task)

        self.link_output_listbox = Listbox(
            create_dataset_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            width=self.configuration.app_listbox_size,
            exportselection=False
        )

        # Fetch the dpi
        dpi = self.app.winfo_fpixels('1i')

        # Create Dataset tab UI layouts
        self.dataset_log_listbox.pack(side="top",
                                      anchor="se",
                                      fill="both",
                                      padx=self.configuration.app_padding,
                                      pady=self.configuration.app_padding,
                                      expand=False)

        self.source_plot_figure = Figure(figsize=(
            int(self.configuration.window_width * self.configuration.app_plot_width / dpi),
            int(self.configuration.window_height * self.configuration.app_plot_height / dpi)),
            dpi=dpi if platform.system() == 'Darwin' else None,
            facecolor=self.configuration.app_dark_background_color)

        self.source_plot_canvas = FigureCanvasTkAgg(self.source_plot_figure,
                                                    create_dataset_tab)

        self.source_plot_canvas.get_tk_widget().pack(side="right",
                                                     anchor="se",
                                                     fill="both",
                                                     expand=False)
        tasks_label.pack(side="top",
                         anchor="nw",
                         padx=self.configuration.app_padding,
                         pady=self.configuration.app_padding,
                         expand=False)

        self.task_listbox.pack(side="top",
                               fill='x',
                               anchor="center",
                               padx=self.configuration.app_padding,
                               pady=self.configuration.app_padding,
                               expand=False)

        import_task_button.pack(side="top",
                                fill='x',
                                anchor="center",
                                padx=self.configuration.app_padding,
                                pady=self.configuration.app_padding,
                                expand=False)

        add_task_button.pack(side="top",
                             fill='x',
                             anchor="center",
                             padx=self.configuration.app_padding,
                             pady=self.configuration.app_padding,
                             expand=False)

        remove_task_button.pack(side="top",
                                fill='x',
                                anchor="center",
                                padx=self.configuration.app_padding,
                                pady=self.configuration.app_padding,
                                expand=False)

        link_output_label.pack(side="top",
                               fill='x',
                               anchor="nw",
                               padx=self.configuration.app_padding,
                               pady=self.configuration.app_padding,
                               expand=False)

        self.link_output_listbox.pack(side="top",
                                      fill='x',
                                      anchor="center",
                                      padx=self.configuration.app_padding,
                                      pady=self.configuration.app_padding,
                                      expand=False)

        link_output_button.pack(side="top",
                                fill='x',
                                anchor="center",
                                padx=self.configuration.app_padding,
                                pady=self.configuration.app_padding,
                                expand=False)

        undo_linking_button.pack(side="top",
                                 fill='x',
                                 anchor="center",
                                 padx=self.configuration.app_padding,
                                 pady=self.configuration.app_padding,
                                 expand=False)

        load_dataset_button.pack(side="bottom",
                                 fill='x',
                                 anchor="center",
                                 padx=self.configuration.app_padding,
                                 pady=self.configuration.app_padding,
                                 expand=False)

        create_dataset_button.pack(side="bottom",
                                   fill='x',
                                   anchor="center",
                                   padx=self.configuration.app_padding,
                                   pady=self.configuration.app_padding,
                                   expand=False)
