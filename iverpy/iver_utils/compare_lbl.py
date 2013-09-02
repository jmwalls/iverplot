import sys
import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lbl_renav import Lbl_beacon, Lbl_fixer
from deif_lcmlog import Pose_estimate

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <lbl.pkl> <est.pkl>' % sys.argv[0]
        sys.exit (0)

    # unpickle
    with open (sys.argv[1], 'rb') as f:
        lbl = pickle.load (f)

    with open (sys.argv[2], 'rb') as f:
        est = pickle.load (f)

    # interpolate estimate to lbl pings
    x_e = np.interp (lbl.sol_utime, est.pose.utime, est.pose.xyzrph[:,0])
    y_e = np.interp (lbl.sol_utime, est.pose.utime, est.pose.xyzrph[:,1])
    xy_e = np.vstack ((x_e,y_e))
    
    dxy = xy_e - lbl.sol
    dx = (dxy[0,:]**2 + dxy[1,:]**2)**(1./2)

    # plot everything
    fig = plt.figure (figsize=(9,9))
    ax = fig.add_subplot (111)
    
    ax.plot (lbl.sol[1,:], lbl.sol[0,:], 'bo-')
    est.plot (ax, 'r')

    ax.axis ('equal')
    ax.grid ()

    fig_comp = plt.figure (figsize=(15,9))
    ax_comp = fig_comp.add_subplot (111)

    ax_comp.plot ((lbl.sol_utime-lbl.sol_utime[0])*1e-6, dx, '.-')

    plt.show ()

    sys.exit (0)
