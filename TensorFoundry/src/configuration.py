import glob

from screeninfo import get_monitors


class Configuration:
    def __init__(self):
        # Application
        self.screen_resolutions = [(monitor.width, monitor.height) for monitor in get_monitors()]
        self.window_size = 0.85
        self.window_width = int(min(monitor[0] for monitor in self.screen_resolutions) * self.window_size)
        self.window_height = int(min(monitor[1] for monitor in self.screen_resolutions) * self.window_size)
        self.refresh_rate = 100

        # Colours
        self.app_light_background_color = "#2E2E2E"
        self.app_dark_background_color = "#1E1E1E"
        self.app_text_foreground_color = "#FFFFEE"
        self.app_select_background_color = "#004E4E"
        self.app_select_foreground_color = "#FFFFFF"

        # Sizes (pixels, text units or percentages)
        self.app_image_size = 300
        self.app_button_size = 23
        self.app_spinbox_size = 25
        self.app_listbox_size = 27
        self.app_plot_width = 0.83
        self.app_plot_height = 0.75
        self.app_padding = 5

        # Logging
        self.log_limit = 1000
        self.log_rate = 10

        # Model
        self.input_size = 128
        self.num_channels = 3

        # Training
        self.epoch_count = 1000
        self.min_dataset_size = 20

        # Read the config file
        self.read_config()

    # Method which reads configuration from file
    def read_config(self):

        files = glob.glob("*.conf")
        for file in files:

            with open(file, "r") as config_file:
                for line in config_file:
                    line = line.strip()

                    # Sanity check for invalid lines
                    if ":" not in line and "=" not in line:
                        continue

                    # Read and format the values
                    config, value = line.replace(":", "=").split('=')
                    value = value.strip().replace('"', '').replace("'", '')

                    # Application
                    if "WINDOW_SIZE" in config.upper():
                        self.window_size = float(value)

                    if "REFRESH_RATE" in config.upper():
                        self.window_size = int(value)

                    # Colors
                    if "APP_LIGHT_BACKGROUND_COLOR" in config.upper():
                        self.app_light_background_color = value

                    if "APP_DARK_BACKGROUND_COLOR" in config.upper():
                        self.app_dark_background_color = value

                    if "APP_TEXT_FOREGROUND_COLOR" in config.upper():
                        self.app_text_foreground_color = value

                    if "APP_SELECT_BACKGROUND_COLOR" in config.upper():
                        self.app_select_background_color = value

                    if "APP_SELECT_FOREGROUND_COLOR" in config.upper():
                        self.app_select_foreground_color = value

                    # Sizes
                    if "APP_IMAGE_SIZE" in config.upper():
                        self.app_image_size = int(value)

                    if "APP_BUTTON_SIZE" in config.upper():
                        self.app_button_size = int(value)

                    if "APP_SPINBOX_SIZE" in config.upper():
                        self.app_spinbox_size = int(value)

                    if "APP_LISTBOX_SIZE" in config.upper():
                        self.app_listbox_size = int(value)

                    if "APP_PLOT_WIDTH" in config.upper():
                        self.app_plot_width = float(value)

                    if "APP_PLOT_HEIGHT" in config.upper():
                        self.app_plot_height = float(value)

                    if "APP_PADDING" in config.upper():
                        self.app_padding = int(value)

                    # Logging
                    if "LOG_LIMIT" in config.upper():
                        self.log_limit = int(value)

                    if "LOG_RATE" in config.upper():
                        self.log_rate = int(value)

                    # Inputs
                    if "MAX_VALUE" in config.upper():
                        self.max_value = int(value)

                    # Model
                    if "INPUT_SIZE" in config.upper():
                        self.input_size = int(value)

                    if "NUM_CHANNELS" in config.upper():
                        self.num_channels = int(value)

                    # Training
                    if "EPOCH_COUNT" in config.upper():
                        self.epoch_count = int(value)

                    if "MIN_DATASET_SIZE" in config.upper():
                        self.min_dataset_size = int(value)

        return
