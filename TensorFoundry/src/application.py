import queue
from datetime import datetime
from tkinter import ttk

from ttkthemes.themed_tk import ThemedTk

from create_dataset import CreateDataset
from create_model import CreateModel
from dataset_preview import DatasetPreview
from configuration import Configuration
from tensorflow_model import TensorflowModel
from train_model import TrainModel

# TODO: CoreMLTools remains incompatible with Tensorflow 2.19.0

class Application:
    def __init__(self):

        # First read configuration
        self.configuration = Configuration()

        # Creating the TKInter window as application
        self.app = ThemedTk(theme="black")
        self.app.title("TensorFoundry v0.1")
        self.app.minsize(self.configuration.window_width, self.configuration.window_height)
        self.app.maxsize(self.configuration.window_width, self.configuration.window_height)
        self.app.resizable(False, False)

        # Setting up the rest of the application objects
        self.log_queue = queue.Queue()
        self.notebook = ttk.Notebook(self.app)
        self.create_model_tab = ttk.Frame(self.notebook)
        self.crate_dataset_tab = ttk.Frame(self.notebook)
        self.train_model_tab = ttk.Frame(self.notebook)
        self.dataset_preview_tab = ttk.Frame(self.notebook)

        self.tensorflow_model = TensorflowModel(
            self.configuration,
            self.log_message,
            self.refresh_application
        )

        self.create_model = CreateModel(
            self.app,
            self.configuration,
            self.log_message,
            self.tensorflow_model
        )

        self.create_dataset = CreateDataset(
            self.app,
            self.configuration,
            self.log_message,
            self.tensorflow_model
        )

        self.dataset_preview = DatasetPreview(
            self.app,
            self.configuration,
            self.log_message
        )

        self.train_model = TrainModel(
            self.app,
            self.configuration,
            self.log_message,
            self.dataset_preview.plot_dataset,
            self.create_model.output_size,
            self.tensorflow_model
        )

        # Create the application UI
        self.create_application_ui()
        self.create_model.create_model_ui(self.create_model_tab)
        self.create_dataset.create_dataset_ui(self.crate_dataset_tab)
        self.train_model.create_train_model_ui(self.train_model_tab)
        self.dataset_preview.create_dataset_preview_ui(self.dataset_preview_tab)

        # Initialize the data
        self.create_model.add_default_outputs()

        # Print a welcome message
        self.log_message("Application started... Welcome!")
        self.print_log()

        # Start the application
        self.app.mainloop()

    def refresh_application(self):
        self.app.update()

    # Method for logging a message
    def log_message(self, message):
        current_time = datetime.now()
        timestamp_str = current_time.strftime("%H:%M:%S.%f")[:-3]

        log_entry = timestamp_str + " " + message

        self.log_queue.put(log_entry)
        self.refresh_application()

    # Method for printing messages into log from the queue
    def print_log(self):
        try:
            messages = self.log_queue.get(0)
            messages = messages.split('\n')

            self.create_model.print_model_log(messages)
            self.create_dataset.print_dataset_log(messages)
            self.train_model.print_training_log(messages)
            self.app.after(self.configuration.log_rate, self.print_log)

        except queue.Empty:
            self.app.after(self.configuration.log_rate, self.print_log)

    # Method which creates the UI
    def create_application_ui(self):

        # Style settings
        style = ttk.Style()
        style.configure(
            "TFrame",
            background=self.configuration.app_light_background_color
        )

        style.configure(
            "TNotebook",
            background=self.configuration.app_light_background_color
        )

        style.configure(
            "TNotebook.Tab",
            background=self.configuration.app_dark_background_color,
            foreground=self.configuration.app_text_foreground_color
        )

        style.map("TNotebook.Tab",
                  background=[("active", self.configuration.app_select_background_color),
                              ("selected", self.configuration.app_select_background_color)],
                  foreground=[("active", self.configuration.app_select_foreground_color),
                              ("selected", self.configuration.app_select_foreground_color)])

        style.configure(
            "TButton",
            anchor="center",
            background=self.configuration.app_light_background_color,
            foreground=self.configuration.app_text_foreground_color
        )

        style.map("TButton",
                  anchor="center",
                  background=[("active", self.configuration.app_select_background_color)],
                  foreground=[("active", self.configuration.app_select_foreground_color)])

        style.configure(
            "TLabel",
            background=self.configuration.app_light_background_color,
            foreground=self.configuration.app_text_foreground_color
        )

        style.configure(
            "TSpinbox",
            fieldbackground=self.configuration.app_dark_background_color,
            foreground=self.configuration.app_text_foreground_color
        )

        # Tab layout
        self.notebook.add(self.create_model_tab, text="Create Model")
        self.notebook.add(self.crate_dataset_tab, text="Create Dataset")
        self.notebook.add(self.train_model_tab, text="Train Model")
        self.notebook.add(self.dataset_preview_tab, text="Dataset Preview")
        self.notebook.pack(fill="both", expand=True)


if __name__ == '__main__':
    Application()
