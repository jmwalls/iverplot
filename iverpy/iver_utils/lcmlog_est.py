import numpy as np
import matplotlib.pyplot as plt

import lcm
from perls_lcmlog import *
from plot_utils import draw_covariance

class Pose_estimate (object):
    """
    time series of iver pose estimates
    """
    def __init__ (self, logfile, channel):
        print '{Iver} parsing estimator events...'
        log = lcm.EventLog (logfile)
        self.pose = parse_from_lcm (log, channel, Position_series)

    def plot (self, ax, *args, **kwargs):
        ax.plot (self.pose.xyzrph[:,1], self.pose.xyzrph[:,0], *args, **kwargs)
        cov_ind = [0,1,6,7]
        #for ii, (xy,cov) in enumerate (zip (self.pose.xyzrph[:,:2], self.pose.xyzrph_cov[:,cov_ind])):
        #    if ii%250: continue
        #    sig = cov.reshape ((2,2))
        #    draw_covariance (ax, xy, sig, 9., *args, **kwargs)


if __name__ == '__main__':
    import sys
    import cPickle as pickle

    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog | est.pkl>' % sys.argv[0]
        sys.exit (0)

    if 'pkl' in sys.argv[1]:
        with open (sys.argv[1], 'rb') as f:
            est = pickle.load (f)
    else:
        #est = Pose_estimate (sys.argv[1], 'SERVER_FILTER_TEST')
        est = Pose_estimate (sys.argv[1], 'CLIENT_FILTER_TEST')
        with open ('est.pkl', 'wb') as f:
            pickle.dump (est, f)

    fig = plt.figure ()

    ax = fig.add_subplot (111)
    est.plot (ax, 'b')
    ax.axis ('equal')
    ax.grid ()

    plt.show ()

    sys.exit (0)
