from base import *

class Depth_plot (Plot_object):
    def __init__ (self, uvclog, lcmlog):
        super (Plot_object, self).__init__ (uvclog, lcmlog)

    def plot (self, ax, xmin, xmax):
        ax.plot ()
        ax.set_ylabel ('depth [m]')
        ax.set_xlim (0,1)

    def set_limits (self, ax):
        ax.set_xlim (0,1)
