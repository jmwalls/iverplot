import sys

import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt

import lcm
from lcmlog_perls import *
from lcmlog_est import Pose_estimate

from perls.lcmtypes.perllcm import isam2_f_pose_pose_partial_t
from perls.lcmtypes.perllcm import isam2_f_glc_t

if __name__ == '__main__':
    if len (sys.argv) < 4:
        print 'usage: %s <est_ceif.pkl> <est_deif.pkl> <lcmlog-client-gm>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        estc = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        estd = pickle.load (f)

    logc = lcm.EventLog (sys.argv[3])
    f_owtt = [isam2_f_pose_pose_partial_t.decode (e.data) for e in logc if e.channel == 'F_RANGE2D']
    t_ds = np.asarray ([f.utime for f in f_owtt])
    #f_ds = [isam2_f_glc_t.decode (e.data) for e in logc if e.channel == 'F_DS2D']
    #t_ds = np.asarray ([f.utime for f in f_ds])

    # plot paths
    fig_path = plt.figure ()
    ax_path = fig_path.add_subplot (111)

    estc.plot (ax_path, 'b.-', label='CEIF')
    estd.plot (ax_path, 'r.-', label='DEIF')

    ax_path.set_xlabel ('east [m]')
    ax_path.set_ylabel ('north [m]')

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()

    # plot time series norm difference
    ii = np.in1d (estc.pose.utime, estd.pose.utime)
    xyc = estc.pose.xyzrph[ii,:2]
    cov_xxc = estc.pose.xyzrph_cov[ii,0]
    cov_yyc = estc.pose.xyzrph_cov[ii,7]

    jj = np.in1d (estd.pose.utime, estc.pose.utime[ii])
    xyd = estd.pose.xyzrph[jj,:2]
    cov_xxd = estd.pose.xyzrph_cov[jj,0]
    cov_yyd = estd.pose.xyzrph_cov[jj,7]

    ut = estc.pose.utime[ii]

    # norm diff 
    dxy = xyc-xyd
    ndxy = np.sqrt (dxy[:,0]**2 + dxy[:,1]**2)

    print 'mean norm diff between poses = ', ndxy.mean ()
    print 'max norm diff between poses = ', ndxy.max ()

    # norm diff at TOL
    ii = np.in1d (estc.pose.utime, t_ds)
    iic = np.hstack ((ii[1:],ii[-1]))
    xyc = estc.pose.xyzrph[iic,:2]

    jj = np.in1d (estd.pose.utime, t_ds)
    jjc = np.hstack ((jj[1:],jj[-1]))
    xyd = estd.pose.xyzrph[jjc,:2]

    dxy_tol = xyc-xyd
    ndxy_tol = np.sqrt (dxy_tol[:,0]**2 + dxy_tol[:,1]**2)
    print 'mean norm diff between poses @tol = ', ndxy_tol.mean ()
    print 'max norm diff between poses @tol = ', ndxy_tol.max ()


    fig_diff = plt.figure (figsize=(10,7))

    #ax_mean = fig_diff.add_subplot (211)
    ax_mean = fig_diff.add_subplot (111)
    ax_mean.plot (1e-6*(ut-ut[0]), ndxy, 'g', lw=2)

    #ax_mean.vlines (1e-6*(t_owtt-ut[0]),0,2, colors='r', lw=3)
    #ax_mean.vlines (1e-6*(t_ds-ut[0]),0,2, colors='k', lw=3)
    for t in t_ds: ax_mean.axvline (1e-6*(t-ut[0]),c='k',lw=1)

    ax_mean.set_ylabel ('norm difference [m]')
    ax_mean.set_xlabel ('mission time [s]')

    #ax_cov = fig_diff.add_subplot (212)
    #ax_cov.plot (1e-6*(ut-ut[0]), cov_xxc**(1./2), 'b')
    #ax_cov.plot (1e-6*(ut-ut[0]), cov_yyc**(1./2), 'b')
    #ax_cov.plot (1e-6*(ut-ut[0]), cov_xxd**(1./2), 'r--')
    #ax_cov.plot (1e-6*(ut-ut[0]), cov_yyd**(1./2), 'r--')
    #ax_cov.set_ylabel ('$\sigma$ uncertainty [m]')
    #ax_cov.set_xlabel ('mission time [s]')

    plt.show ()

    sys.exit (0)
