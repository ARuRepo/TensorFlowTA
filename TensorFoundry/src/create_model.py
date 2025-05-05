import os
from tkinter import END, ttk, Listbox, IntVar

from PIL import ImageTk, Image

from application_utils import DialogType, filepath_dialog, validate_spinbox
from input_dialog import InputDialog


class CreateModel:
    def __init__(self, app, configuration, log_message, tensorflow_model):
        self.app = app
        self.configuration = configuration
        self.log_message = log_message

        self.tensorflow_model = tensorflow_model
        self.model_log_listbox = None
        self.output_listbox = None
        self.input_var = None
        self.output_var = None

    # Method which logs into the model log listbox
    def print_model_log(self, messages):
        for msg in messages:
            self.model_log_listbox.insert(END, msg)
            self.model_log_listbox.yview(END)

        if self.model_log_listbox.index("end") > self.configuration.log_limit:
            self.model_log_listbox.delete(0)

    def disable_log_selection(self, event):
        self.model_log_listbox.selection_clear(0, END)

    # Method for adding default model outputs at startup
    def add_default_outputs(self):
        self.output_listbox.insert(END, "TRUE")
        self.output_listbox.insert(END, "FALSE")
        self.output_listbox.yview(END)
        return

    # Method for handling the import output button
    def import_output_button(self):

        self.log_message("Please select an output labels file")
        outputs_path, load_outputs = filepath_dialog(self.app,
                                                     DialogType.OPENFILE,
                                                     "Please select an output labels file:",
                                                     [('Outputs file', '.txt')])

        if load_outputs:
            with open(outputs_path, "r") as file:
                lines = [label.strip() for label in file.readlines()]
                self.output_listbox.delete(0, END)
                for line in lines:
                    self.output_listbox.insert(END, line.strip())

    # Method for handling the add output button
    def add_output_button(self):

        self.log_message("Please enter model output name")
        output_name = InputDialog(self.app,
                                  self.configuration, "Output name", "Enter model output name:").result

        if output_name:
            output_name = output_name.upper()
            if output_name in self.output_listbox.get(0, END):
                self.log_message("Output {} already exists!".format(output_name))
                return

            self.output_listbox.insert(END, output_name)
        return

    # Method for handling the remove output button
    def remove_output_button(self):
        selected_index = self.output_listbox.curselection()
        if selected_index:
            self.output_listbox.delete(selected_index)
        return

    # Method which returns the currently set model output size with a sanity check
    def output_size(self):
        output_size = self.output_listbox.size()
        if output_size < 2:
            self.log_message("Model must have at least two outputs defined!")
            return False

        self.output_var = output_size
        return True

    # Method for handling the create model button
    def create_model_button(self):

        if not self.output_size():
            return

        self.log_message("Please save the model")
        model_path, save_model = filepath_dialog(
            self.app,
            DialogType.SAVEFILE,
            "Please save the model:",
            [('Keras models', '.keras')])

        if save_model:
            output_names = self.output_listbox.get(0, END)
            self.tensorflow_model.create_model(self.input_var.get(), self.output_var, model_path, output_names)

    # Method for handling the tflite convert button
    def convert_model_tflite_button(self):

        if not self.output_size():
            return

        self.log_message("Please select a model")
        model_path, load_model = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a model:",
            [('Keras models', '.keras')])

        if load_model:
            self.tensorflow_model.convert_model_tflite(
                model_path)

        # Method for handling the coreml convert button

    def convert_model_coreml_button(self):

        if not self.output_size():
            return

        self.log_message("Please select a model")
        model_path, load_model = filepath_dialog(
            self.app,
            DialogType.OPENFILE,
            "Please select a model:",
            [('Keras models', '.keras')])

        if load_model:
            self.tensorflow_model.convert_model_coreml(
                model_path)

        # Method for handling the quit button

    def quit_button(self):
        self.app.destroy()

    # Method which creates the UI for the Create Model tab
    def create_model_ui(self, create_model_tab):

        # Images
        try:
            create_model_tab_image = ImageTk.PhotoImage(
                Image.open(os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "assets",
                    "model_maker_image.png")
                ).resize((self.configuration.app_image_size, self.configuration.app_image_size)))

        except FileNotFoundError:
            create_model_tab_image = None

        if create_model_tab_image:
            model_image_label = ttk.Label(
                create_model_tab,
                image=create_model_tab_image
            )
        else:
            model_image_label = ttk.Label(
                create_model_tab,
                text="(╯°□°)╯︵ ┻━┻"
            )

        model_image_label.image = create_model_tab_image

        # Labels
        input_label = ttk.Label(
            create_model_tab,
            text="Model input size (.png):"
        )

        output_label = ttk.Label(
            create_model_tab,
            text="Model outputs:"
        )

        # Buttons
        import_output_button = ttk.Button(
            create_model_tab,
            text="Import",
            command=self.import_output_button,
            width=self.configuration.app_button_size
        )

        add_output_button = ttk.Button(
            create_model_tab,
            text="+",
            command=self.add_output_button,
            width=self.configuration.app_button_size
        )

        remove_output_button = ttk.Button(
            create_model_tab,
            text="-",
            command=self.remove_output_button,
            width=self.configuration.app_button_size
        )

        create_model_button = ttk.Button(
            create_model_tab,
            text="Create model",
            command=self.create_model_button,
            width=self.configuration.app_button_size
        )

        convert_model_tflite_button = ttk.Button(
            create_model_tab,
            text="TFLite conversion",
            command=self.convert_model_tflite_button,
            width=self.configuration.app_button_size
        )

        convert_model_coreml_button = ttk.Button(
            create_model_tab,
            text="CoreML conversion",
            command=self.convert_model_coreml_button,
            width=self.configuration.app_button_size
        )

        quit_button = ttk.Button(
            create_model_tab,
            text="Quit",
            command=self.quit_button,
            width=self.configuration.app_button_size
        )

        # List boxes
        self.model_log_listbox = Listbox(
            create_model_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            takefocus=0
        )

        self.model_log_listbox.bind("<<ListboxSelect>>", self.disable_log_selection)

        self.output_listbox = Listbox(
            create_model_tab,
            bg=self.configuration.app_dark_background_color,
            fg=self.configuration.app_text_foreground_color,
            selectbackground=self.configuration.app_select_background_color,
            selectforeground=self.configuration.app_select_foreground_color,
            width=self.configuration.app_listbox_size,
            exportselection=False
        )

        # Spin boxes
        self.input_var = IntVar(value=self.configuration.input_size)
        input_spinbox = ttk.Spinbox(
            create_model_tab,
            from_=1,
            to=999999,
            textvariable=self.input_var,
            width=self.configuration.app_spinbox_size,
            wrap=True
        )

        input_spinbox.config(validate="key", validatecommand=(create_model_tab.register(validate_spinbox), "%P"))

        # Create Model tab UI layout
        self.model_log_listbox.pack(side="right",
                                    anchor="se",
                                    fill="both",
                                    padx=self.configuration.app_padding,
                                    pady=self.configuration.app_padding,
                                    expand=True)

        model_image_label.pack(side="top",
                               anchor="center",
                               padx=self.configuration.app_padding,
                               pady=self.configuration.app_padding,
                               expand=False)

        input_label.pack(side="top",
                         anchor="nw",
                         padx=self.configuration.app_padding,
                         pady=self.configuration.app_padding,
                         expand=False)

        input_spinbox.pack(side="top",
                           fill='x',
                           anchor="center",
                           padx=self.configuration.app_padding,
                           pady=self.configuration.app_padding,
                           expand=False)

        output_label.pack(side="top",
                          anchor="nw",
                          padx=self.configuration.app_padding,
                          pady=self.configuration.app_padding,
                          expand=False)

        self.output_listbox.pack(side="top",
                                 fill='x',
                                 anchor="center",
                                 padx=self.configuration.app_padding,
                                 pady=self.configuration.app_padding,
                                 expand=False)

        import_output_button.pack(side="top",
                                  fill='x',
                                  anchor="center",
                                  padx=self.configuration.app_padding,
                                  pady=self.configuration.app_padding,
                                  expand=False)

        add_output_button.pack(side="top",
                               fill='x',
                               anchor="center",
                               padx=self.configuration.app_padding,
                               pady=self.configuration.app_padding,
                               expand=False)

        remove_output_button.pack(side="top",
                                  fill='x',
                                  anchor="center",
                                  padx=self.configuration.app_padding,
                                  pady=self.configuration.app_padding,
                                  expand=False)

        quit_button.pack(side="bottom",
                         fill='x',
                         anchor="center",
                         padx=self.configuration.app_padding,
                         pady=self.configuration.app_padding,
                         expand=False)

        convert_model_coreml_button.pack(side="bottom",
                                         fill='x',
                                         anchor="sw",
                                         padx=self.configuration.app_padding,
                                         pady=self.configuration.app_padding,
                                         expand=False)

        # TODO: This has version incompatibility!
        convert_model_coreml_button['state'] = 'disabled'

        convert_model_tflite_button.pack(side="bottom",
                                         fill='x',
                                         anchor="center",
                                         padx=self.configuration.app_padding,
                                         pady=self.configuration.app_padding,
                                         expand=False)

        create_model_button.pack(side="bottom",
                                 fill='x',
                                 anchor="center",
                                 padx=self.configuration.app_padding,
                                 pady=self.configuration.app_padding,
                                 expand=False)
