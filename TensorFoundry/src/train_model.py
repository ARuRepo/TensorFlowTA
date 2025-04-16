import math
import os
import platform
from tkinter import END, ttk, Listbox, IntVar

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from application_utils import DialogType, filepath_dialog, validate_spinbox
from create_dataset import read_output_labels
from tensorflow_dataset import DataSet


class TrainModel:
    def __init__(self, app, configuration, log_message, plot_dataset, output_size, tensorflow_model):
        self.app = app
        self.configuration = configuration
        self.log_message = log_message
        self.plot_dataset = plot_dataset
        self.output_size = output_size
        self.tensorflow_model = tensorflow_model
        self.training_log_listbox = None
        self.epoch_var = None
        self.training_plot_figure = None
        self.training_plot_canvas = None
        self.training_plot = None

    # Method which logs into the dataset log listbox
    def print_training_log(self, messages):
        for msg in messages:
            self.training_log_listbox.insert(END, msg)
            self.training_log_listbox.yview(END)

        if self.training_log_listbox.index("end") > self.configuration.log_limit:
            self.training_log_listbox.delete(0)

    def disable_log_selection(self, event):
        self.training_log_listbox.selection_clear(0, END)

    # Method for the train button
    def train_model_button(self):

        self.log_message("Please select a model")
        model_path, load_model = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a model:",
            [('Keras models', '.keras')])

        if load_model:

            self.log_message("Please select a dataset directory")
            dataset_path, load_dataset = (
                filepath_dialog(self.app, DialogType.SELECTDIR, "Please select a dataset directory:"))

            model_name = os.path.splitext(os.path.basename(model_path))[0]
            input_size = self.tensorflow_model.get_model_input(model_path)
            class_names, load_classes = read_output_labels(model_name, model_path)

            if load_dataset and load_classes:
                training_dataset = (
                    DataSet(self.configuration,
                            self.log_message,
                            self.plot_dataset,
                            input_size)
                    .create_datasets(dataset_path,
                                     class_names)
                )

                if training_dataset is None:
                    return

                self.log_message("Created datasets for classes {}".format(class_names))

                self.tensorflow_model.stop_training = False
                self.tensorflow_model.train_model(
                    model_path, self.epoch_var, training_dataset, class_names, self.plot_results)

        # Method for the stop training button

    def stop_training_button(self):
        self.tensorflow_model.stop_training = True
        return

        # Method for running prediction for a single input image

    def test_model_button(self):

        if not self.output_size():
            return

        self.log_message("Please select a model")
        model_path, load_model = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a model:",
            [('Keras models', '.keras')])

        if load_model:
            self.log_message("Please select an image")
            image_path, load_image = filepath_dialog(
                self.app,
                DialogType.OPENFILE,
                "Please select an image:",
                [("PNG", ".png")])

            if load_image:
                model_name = os.path.splitext(os.path.basename(model_path))[0]
                input_size = self.tensorflow_model.get_model_input(model_path)

                test_state, class_names = (DataSet(self.configuration, self.log_message, self.plot_dataset, input_size)
                                           .create_test_data(model_name, model_path, image_path))

                self.tensorflow_model.test_model(
                    model_path, test_state, class_names)

    def calculate_epoch_interval(self):
        return max(math.floor(self.epoch_var.get() / 10), 1)

    # Method which plots the scores and mean_scores into the graph
    def plot_results(self, accuracy, loss):
        self.training_plot.clear()
        self.training_plot.set_title(label="Training epochs", color=self.configuration.app_text_foreground_color)
        self.training_plot.set_xlabel("Epoch")
        self.training_plot.xaxis.label.set_color(self.configuration.app_text_foreground_color)
        self.training_plot.set_ylabel("Accuracy / Loss")
        self.training_plot.yaxis.label.set_color(self.configuration.app_text_foreground_color)
        self.training_plot.plot(accuracy, label="Accuracy")
        self.training_plot.plot(loss, label="Loss")
        self.training_plot.legend(loc="upper left")
        self.training_plot.set_ylim(ymin=0)
        self.training_plot.text(len(accuracy) - 1, accuracy[-1], str(accuracy[-1]),
                                color=self.configuration.app_text_foreground_color)
        self.training_plot.text(len(loss) - 1, loss[-1], str(loss[-1]),
                                color=self.configuration.app_text_foreground_color)
        self.training_plot.set_xticks(range(0, self.epoch_var.get() + 1, self.calculate_epoch_interval()))
        self.training_plot_canvas.draw()

    # Method which creates the UI for the Train Model tab
    def create_train_model_ui(self, train_model_tab):

        # Labels
        epoch_label = ttk.Label(
            train_model_tab,
            text="Number of epochs:"
        )

        # Buttons
        train_model_button = ttk.Button(
            train_model_tab,
            text="Train model",
            command=self.train_model_button,
            width=self.configuration.app_button_size
        )

        stop_training_button = ttk.Button(
            train_model_tab,
            text="Stop training",
            command=self.stop_training_button,
            width=self.configuration.app_button_size
        )

        test_model_button = ttk.Button(
            train_model_tab,
            text="Test model",
            command=self.test_model_button,
            width=self.configuration.app_button_size
        )

        # List boxes
        self.training_log_listbox = Listbox(
            train_model_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            takefocus=0
        )

        self.training_log_listbox.bind("<<ListboxSelect>>", self.disable_log_selection)

        # Spin boxes
        self.epoch_var = IntVar(value=self.configuration.epoch_count)
        epoch_spinbox = ttk.Spinbox(
            train_model_tab,
            from_=1,
            to=999999,
            textvariable=self.epoch_var,
            width=self.configuration.app_spinbox_size,
            wrap=True
        )

        epoch_spinbox.config(validate="key", validatecommand=(train_model_tab.register(validate_spinbox), "%P"))

        # Fetch the dpi
        dpi = self.app.winfo_fpixels('1i')

        # Train model tab UI layout
        self.training_plot_figure = Figure(figsize=(
            int(self.configuration.window_width * self.configuration.app_plot_width / dpi),
            int(self.configuration.window_height * self.configuration.app_plot_height / dpi)),
            dpi=dpi if platform.system() == 'Darwin' else None,
            facecolor=self.configuration.app_dark_background_color)

        self.training_plot = self.training_plot_figure.add_subplot(
            1, 1, 1, facecolor=self.configuration.app_dark_background_color)
        self.training_plot_canvas = FigureCanvasTkAgg(self.training_plot_figure, train_model_tab)
        self.training_plot.set_xticks(range(0, self.epoch_var.get() + 1, self.calculate_epoch_interval()))
        self.training_plot.tick_params(axis='x', colors=self.configuration.app_text_foreground_color)
        self.training_plot.tick_params(axis='y', colors=self.configuration.app_text_foreground_color)
        self.training_plot.spines['bottom'].set_color(self.configuration.app_text_foreground_color)
        self.training_plot.spines['top'].set_color(self.configuration.app_text_foreground_color)
        self.training_plot.spines['right'].set_color(self.configuration.app_text_foreground_color)
        self.training_plot.spines['left'].set_color(self.configuration.app_text_foreground_color)

        self.training_log_listbox.pack(side="top",
                                       anchor="se",
                                       fill="both",
                                       padx=self.configuration.app_padding,
                                       pady=self.configuration.app_padding,
                                       expand=True)

        self.training_plot_canvas.get_tk_widget().pack(side="right",
                                                       anchor="se",
                                                       fill="both",
                                                       expand=False)

        epoch_label.pack(side="top",
                         anchor="nw",
                         padx=self.configuration.app_padding,
                         pady=self.configuration.app_padding,
                         expand=False)

        epoch_spinbox.pack(side="top",
                           fill='x',
                           anchor="center",
                           padx=self.configuration.app_padding,
                           pady=self.configuration.app_padding,
                           expand=False)

        test_model_button.pack(side="bottom",
                               fill='x',
                               anchor="center",
                               padx=self.configuration.app_padding,
                               pady=self.configuration.app_padding,
                               expand=False)

        stop_training_button.pack(side="bottom",
                                  fill='x',
                                  anchor="center",
                                  padx=self.configuration.app_padding,
                                  pady=self.configuration.app_padding,
                                  expand=False)

        train_model_button.pack(side="bottom",
                                fill='x',
                                anchor="center",
                                padx=self.configuration.app_padding,
                                pady=self.configuration.app_padding,
                                expand=False)
