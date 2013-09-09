import sys

import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt

from est_lcmlog import Pose_estimate

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <est0.pkl> <est1.pkl>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        est0 = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        est1 = pickle.load (f)

    # plot paths
    fig_path = plt.figure ()
    ax_path = fig_path.add_subplot (111)

    est0.plot (ax_path, 'b', label='first')
    est1.plot (ax_path, 'r', label='second')

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()

    # plot time series norm difference
    ii = np.in1d (est0.pose.utime, est1.pose.utime)
    xy0 = est0.pose.xyzrph[ii,:2]
    cov_xx0 = est0.pose.xyzrph_cov[ii,0]
    cov_yy0 = est0.pose.xyzrph_cov[ii,7]

    jj = np.in1d (est1.pose.utime, est0.pose.utime[ii])
    xy1 = est1.pose.xyzrph[jj,:2]
    cov_xx1 = est1.pose.xyzrph_cov[jj,0]
    cov_yy1 = est1.pose.xyzrph_cov[jj,7]

    ut = est0.pose.utime[ii]

    dxy = xy0-xy1
    ndxy = (dxy[:,0]**2 + dxy[:,1]**2)**(1./2)

    fig_diff = plt.figure ()
    ax_mean = fig_diff.add_subplot (211)
    ax_mean.plot (1e-6*(ut-ut[0]), ndxy, 'g', lw=2)

    ax_cov = fig_diff.add_subplot (212)
    ax_cov.plot (1e-6*(ut-ut[0]), cov_xx0**(1./2), 'r')
    ax_cov.plot (1e-6*(ut-ut[0]), cov_yy0**(1./2), 'r')
    ax_cov.plot (1e-6*(ut-ut[0]), cov_xx1**(1./2), 'b--')
    ax_cov.plot (1e-6*(ut-ut[0]), cov_yy1**(1./2), 'b--')


    plt.show ()

    sys.exit (0)
