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

    #### get topside GPS
    #from perls import BotParam
    #from perls import BotCore
    #with open (sys.argv[3], 'rb') as f:
    #    topside = pickle.load (f)
    #param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/iver28.cfg', 'false', '')
    #param = BotParam.BotParam (param_args)
    #orglatlon = param.get_double_array ('site.orglatlon')
    #llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])
    #lat = topside.gpsd.fix.latitude
    #lon = topside.gpsd.fix.longitude
    #y_lst, x_lst = [],[]
    #for la, lo in zip (lat, lon):
    #    y,x = llxy.to_xy (la*180./np.pi, lo*180./np.pi)
    #    y_lst.append (y)
    #    x_lst.append (x)
    #xy_topside = np.column_stack ((x_lst, y_lst))

    # find client nodes
    ii = np.where (sol.nodes > 1e5)[0] # client nodes
    #ii = np.where (sol.nodes < 1e5)[0] # server nodes
    nodes = sol.nodes[ii]

    ii = np.in1d (isam.id, nodes)
    nodes = isam.id[ii]

    # sol0 xy
    ii = np.in1d (sol.nodes, nodes)
    xy_deif = sol.x[ii,:]
    sig_deif = sol.cov[ii,:]

    # sol1 xy
    ii = np.in1d (isam.id, nodes)
    xy_isam = isam.mu[ii,:]
    sig_isam = isam.cov[ii,:]

    # compute difference
    dxy = xy_deif-xy_isam
    ndxy = np.sqrt (dxy[:,0]**2 + dxy[:,1]**2)

    print 'mean norm diff between poses = ', ndxy.mean ()
    print 'max norm diff between poses = ', ndxy.max ()

    # plot everything
    fig_path = plt.figure ()
    ax_path = fig_path.add_subplot (111)
    
    ax_path.plot (xy_deif[:,1], xy_deif[:,0], 'b.-', label='DEIF', lw=2)
    ax_path.plot (xy_isam[:,1], xy_isam[:,0], 'r.-', label='iSAM')

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()

    fig_diff = plt.figure (figsize=(10,5))
    ax_diff = fig_diff.add_subplot (111)

    t = (nodes-nodes[0])*1e-6
    ax_diff.plot (t, ndxy, 'b.-')

    ax_diff.set_xlabel ('Client node id')
    ax_diff.set_ylabel ('Norm difference [m]')

    fig_diff.savefig ('isamcomp.pdf', transparent=True, bbox_inches='tight',
            pad_inches=0)

    #fig_sig = plt.figure ()
    #ax_sig = fig_sig.add_subplot (111)
    #ax_sig.plot (sig_deif[:,0], 'r')
    #ax_sig.plot (sig_isam[:,0], 'b--')

    plt.show ()

    sys.exit (0)
