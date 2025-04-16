import os
from enum import Enum
from tkinter import filedialog


class DialogType(Enum):
    OPENFILE = 1
    SAVEFILE = 2
    SELECTDIR = 3


def filepath_dialog(app, dialog_type, title, filetypes=("All Files", "*.*")):
    model_path = ""

    if dialog_type == DialogType.OPENFILE:
        model_path = filedialog.askopenfilename(parent=app,
                                                initialdir=os.getcwd(),
                                                title=title,
                                                filetypes=filetypes)

    if dialog_type == DialogType.SAVEFILE:
        model_path = filedialog.asksaveasfilename(parent=app,
                                                  initialdir=os.getcwd(),
                                                  title=title,
                                                  filetypes=filetypes)

    if dialog_type == DialogType.SELECTDIR:
        model_path = filedialog.askdirectory(parent=app,
                                             initialdir=os.getcwd(),
                                             title=title)

    if model_path == () or model_path == "":
        return "", False

    return model_path, True


# Function for reading the model output labels as actions for linking to a task
def read_output_labels(model_name, model_path):
    labels_path = os.path.join(os.path.dirname(model_path), f"{model_name}_output_labels.txt")

    # If the file does not exist we return None and False
    if not os.path.isfile(labels_path):
        return None, False

    with open(labels_path, "r") as file:
        return [label.strip() for label in file.readlines()], True


# Function for reading the model output labels as actions for linking to a task
def read_task_labels(dataset_path):
    tasks_path = os.path.join(dataset_path, "dataset_tasks.txt")

    # If the file does not exist we return None and False
    if not os.path.isfile(tasks_path):
        return None, False

    with open(tasks_path, "r") as file:
        return [label.strip() for label in file.readlines()], True


# Method for validating a spinbox input
def validate_spinbox(user_input):
    if user_input.isdigit():
        minvalue = 1
        maxvalue = 999999
        if int(user_input) not in range(minvalue, maxvalue + 1):  # Include the max value
            return False

        return True

    elif user_input == "":
        return True

    else:
        return False
