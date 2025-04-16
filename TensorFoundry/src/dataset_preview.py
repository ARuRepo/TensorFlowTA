import platform

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DatasetPreview:
    def __init__(self, app, configuration, log_message):
        self.app = app
        self.configuration = configuration
        self.log_message = log_message
        self.dataset_plot_figure = None
        self.dataset_plot_canvas = None
        self.dataset_plot = None

    # Method which plots some dataset preview images
    def plot_dataset(self, dataset):
        self.dataset_plot_figure.clear()
        for images, labels in dataset.take(1):
            for i in range(16):
                self.dataset_plot = self.dataset_plot_figure.add_subplot(4, 4, i + 1)
                self.dataset_plot.imshow(images[i].numpy().astype("uint8"))
                self.dataset_plot.set_title(dataset.class_names[labels[i]],
                                            color=self.configuration.app_text_foreground_color)
                self.dataset_plot.axis("off")
        self.dataset_plot_figure.tight_layout()
        self.dataset_plot_canvas.draw()

    # Method which creates the UI for the Dataset Preview tab
    def create_dataset_preview_ui(self, dataset_preview_tab):

        # Fetch the dpi
        dpi = self.app.winfo_fpixels('1i')

        # Dataset Preview tab UI layout
        self.dataset_plot_figure = Figure(figsize=(int(self.configuration.window_width / dpi),
                                                   int(self.configuration.window_height / dpi)),
                                          dpi=dpi if platform.system() == 'Darwin' else None,
                                          facecolor=self.configuration.app_dark_background_color)
        self.dataset_plot_canvas = FigureCanvasTkAgg(self.dataset_plot_figure, dataset_preview_tab)
        self.dataset_plot_canvas.get_tk_widget().pack(fill="both",
                                                      padx=self.configuration.app_padding,
                                                      pady=self.configuration.app_padding,
                                                      expand=False)
