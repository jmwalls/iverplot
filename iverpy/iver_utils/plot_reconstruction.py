#!/usr/bin/env python
import sys
import cPickle as pickle

from lcmlog_perls import *
from osm_pose_chain import *

import matplotlib.pyplot as plt
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=14)

if __name__ == '__main__':
    if len (sys.argv) < 4:
        print 'usage: %s <server_iver.pkl> <client_iver.pkl> <lcmlog-server-isam>' % sys.argv[0]
        sys.exit (0)

    try:
        with open (sys.argv[1], 'rb') as f:
            server = pickle.load (f)
        server_osm = iver_to_osm_series (server.osm)

        with open (sys.argv[2], 'rb') as f:
            client = pickle.load (f)
        client_osm = iver_to_osm_series (client.osm)

        log = lcm.EventLog (sys.argv[3])
        server_isam = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)
    except Exception as err:
        print 'error loading pickles: %s' % err
        sys.exit (0)

    client_pc = client_osm.pc[-1]

    # find the server pose chain that has the same last id
    for server_pc in reversed (server_osm.pc):
        if server_pc.ids[-1]==client_pc.ids[-1]: break

    xy_server = server_isam.mu[:,:2]

    # plot the pose chains
    fig = plt.figure ()
    ax = fig.add_subplot (111)

    ax.plot (xy_server[:,1], xy_server[:,0], c='0.70', lw=4)
    server_pc.plot (ax, 'k', lw=2)
    client_pc.plot (ax, 'r', lw=4)

    lsf = ax.lines[0]
    lst = ax.lines[1]
    lc = ax.lines[-1]

    ax.set_xlabel ('East [m]')
    ax.set_ylabel ('North [m]')

    ax.axis ('equal')
    ax.grid ()
    ax.legend ((lsf,lst,lc), ('Server Full', 'Server TOL', 'Client'))

    fig.savefig ('pgreconstruct.pdf', transparent=True, bbox_inches='tight',
            pad_inches=0)
    plt.show ()

    sys.exit (0)
