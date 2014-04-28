import numpy as np

class Median_filter (object):
    """
    generic median filter object for scalar values

    Parameters
    -----------
    win_size : size of window to compute threshold
    median_threshold : threshold for median test
    vals : list of raw values
    is_good : vector of whether a measurement was accepted or not
    """
    def __init__ (self, win_size, median_threshold):
        self.win_size = win_size
        self.median_threshold = median_threshold
        self.utime = []
        self.vals = []
        self.is_good = []

    def add_value (self, utime, val):
        """
        add new value

        Parameters
        -----------

        Returns
        --------
        true : if value passes the median test
        false : if the value does not pass the median test or not enough
            measurements have been collected
        """
        self.utime.append (utime)

        if len (self.vals) <  self.win_size:
            self.vals.append (val)
            self.is_good.append (0)
            return False

        med = np.median (self.vals[-self.win_size:])
        self.vals.append (val)

        if abs (med - val) < self.median_threshold:
            self.is_good.append (1)
            return True
        self.is_good.append (0)
        return False
