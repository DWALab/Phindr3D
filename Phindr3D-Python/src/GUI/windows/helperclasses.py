# These classes are not windows, but help build other features in windows
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection=="3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111, projection=None)
        super(MplCanvas, self).__init__(self.fig)

#imported matplotlib toolbar. Only use desired functions.
class NavigationToolbar(NavigationToolbar):
    NavigationToolbar.toolitems = (
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Customize', 'Edit axis, curve and image parameters', 'qt4_editor_options', 'edit_parameters'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure')
    )

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe

#zoom in/out fixed xy plane
class fixed_2d():
    def __init__(self, main_plot, sc_plot, projection):
        self.main_plot =main_plot
        self.sc_plot =sc_plot
        self.projection = projection

    def __call__(self, event):

        if event.inaxes is not None:
            if self.projection=="2d":
                if event.button == 'up':
                    self.main_plot.axes.mouse_init()
                    self.main_plot.axes.xaxis.zoom(-1)
                    self.main_plot.axes.yaxis.zoom(-1)
                    self.main_plot.axes.zaxis.zoom(-1)
                if event.button =='down':
                    self.main_plot.axes.xaxis.zoom(1)
                    self.main_plot.axes.yaxis.zoom(1)
                    self.main_plot.axes.zaxis.zoom(-1)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()