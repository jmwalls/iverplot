import sys

import cPickle as pickle
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=18)

from centralized_filter import Centralized_solution
from lcmlog_perls import *
from osm_pose_chain import *

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <sol_client.pkl> <lcmlog-isam>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        sol = pickle.load (f)

    log = lcm.EventLog (sys.argv[2])
    isam = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)

    # sol0 xy
    ii = np.where (sol.nodes > 1e5)[0] # client nodes
    xy_deif = sol.x[ii,:]
    t_deif = sol.nodes[ii]

    # sol1 xy
    ii = np.where (isam.id > 1e5)[0] # client nodes
    xy_isam = isam.mu[ii,:]
    t_isam = isam.id[ii]

    # interp isam solution at deif
    x_t = np.interp (t_deif, t_isam, xy_isam[:,0])
    y_t = np.interp (t_deif, t_isam, xy_isam[:,1])
    xy_t = np.column_stack ((x_t,y_t))

    ## compute difference
    dxy = xy_deif-xy_t
    ndxy = np.sqrt (dxy[:,0]**2 + dxy[:,1]**2)

    print 'mean norm diff between poses = ', ndxy.mean ()
    print 'max norm diff between poses = ', ndxy.max ()

    # plot everything
    fig_path = plt.figure ()
    ax_path = fig_path.add_subplot (111)
    
    ax_path.plot (xy_isam[:,1], xy_isam[:,0], '-', label='iSAM', color='0.70', lw=5)
    ax_path.plot (xy_deif[:,1], xy_deif[:,0], '-', label='DEIF', color='0.01', lw=2)

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()

    fig_diff = plt.figure (figsize=(10,5))
    ax_diff = fig_diff.add_subplot (111)

    t = (t_deif-t_deif[0])*1e-6
    ax_diff.plot (t, ndxy, 'b.-')

    #ax_diff.set_xlabel ('Client node id')
    #ax_diff.set_ylabel ('Norm difference [m]')

    plt.show ()

    sys.exit (0)
