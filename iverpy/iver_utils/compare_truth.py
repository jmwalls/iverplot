import sys
import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lcmlog_est import Pose_estimate
from lcmlog_perls import *

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <est.pkl> <lcmlog-truth>' % sys.argv[0]
        sys.exit (0)

    # unpickle estimate
    with open (sys.argv[1], 'rb') as f:
        est = pickle.load (f)

    # get ground truth
    log = lcm.EventLog (sys.argv[2])
    nodes = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)

    ii = np.where (nodes.id > 10e5)[0]
    utime_truth = nodes.id[ii]
    xy_truth = nodes.mu[ii,:2]
    xy_cov = nodes.cov[ii,:]

    # get estimates within the time window that we have ground truth
    ii = np.where ((est.pose.utime >= utime_truth[0]) | (est.pose.utime <= utime_truth[1]))[0]
    utime_est = est.pose.utime[ii]
    xy_e = est.pose.xyzrph[ii,:2]
    cov_e = est.pose.xyzrph_cov[ii,:][:,[0,1,6,7]]

    # interpolate ground truth for estimates
    x_t = np.interp (utime_est, utime_truth, xy_truth[:,0])
    y_t = np.interp (utime_est, utime_truth, xy_truth[:,1])
    xy_t = np.column_stack ((x_t,y_t))

    dxy = xy_e - xy_t
    dn = np.sqrt (dxy[:,0]**2 + dxy[:,1]**2)

    print 'mean norm diff between poses = ', dn.mean ()
    print 'max norm diff between poses = ', dn.max ()

    # plot everything
    # birds-eye view
    fig_birds = plt.figure ()
    ax_birds = fig_birds.add_subplot (111)

    ax_birds.plot (xy_t[:,1], xy_t[:,0], 'b', lw=2, label='Ground truth')
    ax_birds.plot (xy_e[:,1], xy_e[:,0], 'r', lw=1, label='Estimate')

    ax_birds.legend ()
    ax_birds.axis ('equal')
    ax_birds.grid ()

    # difference time-series
    fig_diff = plt.figure (figsize=(10,10))
    ax_xdiff = fig_diff.add_subplot (211)
    ax_ydiff = fig_diff.add_subplot (212)
    #ax_ndiff = fig_diff.add_subplot (313)

    t = (utime_est-utime_est[0])*1e-6
    z = np.zeros (t.shape)
    t_t = (utime_truth-utime_est[0])*1e-6

    ax_xdiff.plot (t, dxy[:,0], 'b', lw=2)
    sigx = np.sqrt (cov_e[:,0])
    ax_xdiff.fill_between (t, 3*sigx, -3*sigx, color='b', alpha=0.2)
    #sigx_t = np.sqrt (xy_cov[:,0])
    #ax_xdiff.fill_between (t_t, 3*sigx_t, -3*sigx_t, color='k', alpha=0.2)
    #ax_xdiff.fill_between (t, dxy[:,0]+3*sigx, dxy[:,0]-3*sigx, color='b', alpha=0.2)
    #ax_xdiff.plot (t, z, 'k', lw=2)

    ax_ydiff.plot (t, dxy[:,1], 'r', lw=2)
    sigy = np.sqrt (cov_e[:,3])
    ax_ydiff.fill_between (t, 3*sigy, -3*sigy, color='r', alpha=0.2)
    #sigy_t = np.sqrt (xy_cov[:,3])
    #ax_ydiff.fill_between (t_t, 3*sigy_t, -3*sigy_t, color='k', alpha=0.2)
    #ax_ydiff.fill_between (t, dxy[:,1]+3*sigy, dxy[:,1]-3*sigy, color='r', alpha=0.2)
    #ax_ydiff.plot (t, z, 'k', lw=2)

    #ax_ndiff.plot (t, dn, 'k', lw=2)
    #sign = (cov_e[:,0]*cov_e[:,3]-cov_e[:,1]*cov_e[:,2])**(1./4)
    #ax_ndiff.fill_between (t, 3*sign, -3*sign, color='k', alpha=0.2)

    ax_xdiff.set_ylabel ('x-error [m]')
    ax_ydiff.set_ylabel ('y-error [m]')
    ax_ydiff.set_xlabel ('mission time [s]')

    plt.show ()

    sys.exit (0)
