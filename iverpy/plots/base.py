"""
Plot interface class definition
"""


class Plot_object (object):
    """
    Plot_object represents the interface class for a specific plot, e.g., a
    time series that plots both depth and altitude, or rph values

    plot object knows how to draw the specific plot including labels, legend,
    etc.

    Parameters
    -----------

    Notes
    ------

    """
    def __init__ (self, uvclog, lcmlog):
        self.uvclog = uvclog
        self.lcmlog = lcmlog

    def plot (self, ax, xmin, xmax):
        ax.clear ()
        if self.uvclog:
            ax.plot (self.uvclog.utime, self.uvclog.dfs_depth, 'r')
        else:
            ax.plot ()
        self.set_limits (ax, xmin, xmax)

    def set_limits (self, ax, xmin, xmax):
        if xmin and xmax: ax.set_xlim (xmin,xmax)
