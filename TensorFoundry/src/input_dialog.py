import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog


class InputDialog(Dialog):
    def __init__(self, parent, configuration, title=None, prompt=""):
        self.result = None
        self.entry = None
        self.prompt = prompt
        self.configuration = configuration
        super().__init__(parent, title)

    # Method which creates the dialog body
    def body(self, master):
        self.configure(background=self.configuration.app_light_background_color)
        master.configure(background=self.configuration.app_light_background_color)

        # Input label
        ttk.Label(master, text=self.prompt, style="TLabel").pack(side="top", padx=5, pady=5, expand=True)

        # Text entry
        self.entry = tk.Entry(master,
                              width=50,
                              background=self.configuration.app_dark_background_color,
                              foreground=self.configuration.app_text_foreground_color)

        self.entry.pack(expand=True)

        # Set focus to this widget
        return self.entry

    # Method which creates the button box
    def buttonbox(self):
        box = ttk.Frame(self)
        ttk.Button(box, text="OK", command=self.ok, style="TButton").pack(side="bottom", padx=5, pady=5)
        box.pack(expand=True)

    # Method which handles the button press
    def apply(self):
        self.result = self.entry.get()
