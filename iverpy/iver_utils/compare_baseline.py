import sys

import cPickle as pickle
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=18)

from centralized_filter import Centralized_solution
from lcmlog_perls import *

if __name__ == '__main__':
    if len (sys.argv) < 4:
        print 'usage: %s <sol.pkl> <lcmlog-lbl> <lcmlog-gps>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        deif = pickle.load (f)

    log = lcm.EventLog (sys.argv[2])
    lbl = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)
    
    log = lcm.EventLog (sys.argv[3])
    gps = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)

    ii = np.where (deif.nodes > 1e5)[0]
    xy_deif = deif.x[ii,:]
    sig_deif = deif.cov[ii,:]
    t_deif = (deif.nodes[ii] - deif.nodes[0])*1e-6
    sigx = np.sqrt (deif.cov[ii,0])
    sigy = np.sqrt (deif.cov[ii,3])

    ii = np.where (lbl.id > 1e5)[0]
    xy_lbl = lbl.mu[ii,:]
    t_lbl = (lbl.id[ii]-deif.nodes[0])*1e-6

    ii = np.where (gps.id > 1e5)[0]
    xy_gps = gps.mu[ii,:]
    t_gps = (gps.id[ii]-deif.nodes[0])*1e-6

    # compute errors relative to gps
    x_deif_t = np.interp (t_deif, t_gps, xy_gps[:,0])
    y_deif_t = np.interp (t_deif, t_gps, xy_gps[:,1])
    xy_deif_t = np.column_stack ((x_deif_t,y_deif_t))

    dxy_deif = xy_deif-xy_deif_t
    ndxy_deif = np.sqrt (dxy_deif[:,0]**2 + dxy_deif[:,1]**2)
    print 'deif mean norm diff between poses = ', ndxy_deif.mean ()
    print 'deif max norm diff between poses = ', ndxy_deif.max ()

    x_lbl_t = np.interp (t_lbl, t_gps, xy_gps[:,0])
    y_lbl_t = np.interp (t_lbl, t_gps, xy_gps[:,1])
    xy_lbl_t = np.column_stack ((x_lbl_t,y_lbl_t))

    dxy_lbl = xy_lbl-xy_lbl_t
    ndxy_lbl = np.sqrt (dxy_lbl[:,0]**2 + dxy_lbl[:,1]**2)
    print 'lbl mean norm diff between poses = ', ndxy_lbl.mean ()
    print 'lbl max norm diff between poses = ', ndxy_lbl.max ()

    # plot everything
    fig = plt.figure (figsize=(8,10))

    ax_path = plt.subplot2grid ((3,2), (0,0), rowspan=2, colspan=2)
    ax_sig = plt.subplot2grid ((3,2), (2,0), rowspan=1, colspan=2)
    
    ax_path.plot (xy_gps[:,1], xy_gps[:,0], '-', label='GPS', color='0.70', lw=5)
    ax_path.plot (xy_lbl[:,1], xy_lbl[:,0], '--', label='LBL', color='0.10', lw=2)
    ax_path.plot (xy_deif[:,1], xy_deif[:,0], '-', label='DEIF', color='0.00', lw=1)

    ax_path.add_artist (Rectangle ((30,-280),85,40,color='r',fill=False,lw=3,zorder=50))
    ax_zoom = fig.add_axes ((0.67,0.45,0.2,0.1),xticks=[],yticks=[],zorder=100)
    for s in ax_zoom.spines.itervalues ():
        s.set_color ('r')
        s.set_linewidth (3)
    ax_zoom.plot (xy_gps[:,1], xy_gps[:,0], '-', label='GPS', color='0.70', lw=5)
    ax_zoom.plot (xy_lbl[:,1], xy_lbl[:,0], '--', label='LBL', color='0.10', lw=2)
    ax_zoom.plot (xy_deif[:,1], xy_deif[:,0], '-', label='DEIF', color='0.00', lw=1)
    ax_zoom.axis ([30,115,-280,-240])

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()
    ax_path.set_xlabel ('East [m]')
    ax_path.set_ylabel ('North [m]')

    ax_sig.plot (t_deif, 3*sigx, 'k-', label='X')
    ax_sig.plot (t_deif, 3*sigy, 'k--', label='Y')

    ax_sig.legend ()
    ax_sig.set_xlabel ('mission time [s]')
    ax_sig.set_ylabel ('3-$\sigma$ uncertainty [m]')

    plt.subplots_adjust (hspace=0.5)
    fig.savefig ('baseline.pdf', transparent=False, bbox_inches='tight',
            pad_inches=0)

    fig_diff = plt.figure (figsize=(10,5))
    ax_diff = fig_diff.add_subplot (111)
    ax_diff.plot (t_deif, ndxy_deif, '-', label='DEIF', color='0.10', lw=2)
    ax_diff.plot (t_lbl, ndxy_lbl, '--', label='LBL', color='0.00', lw=1)
    ax_diff.legend  ()

    plt.show ()

    sys.exit (0)
