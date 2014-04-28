import sys
import cPickle as pickle

import matplotlib.pyplot as plt

import lcm
from lcmlog_perls import *
from plot_utils import draw_covariance

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-isam-client> <lcmlog-isam-server>' % sys.argv[0]
        sys.exit (0)

    try:
        log = lcm.EventLog (sys.argv[1])
        client_nodes = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)

        log = lcm.EventLog (sys.argv[2])
        server_nodes = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)
    except Exception as err:
        print 'error loading lcmlogs: %s' % err
        sys.exit (0)

    ii_client = np.in1d (client_nodes.id, server_nodes.id)
    xy_client = client_nodes.mu[ii_client,:]
    cov_client = client_nodes.cov[ii_client,:]
    print 'client received ids:'
    print client_nodes.id[ii_client]

    ii_server = np.in1d (server_nodes.id, client_nodes.id)
    xy_server = server_nodes.mu[ii_server,:]
    cov_server = server_nodes.cov[ii_server,:]
    print 'server received ids:'
    print server_nodes.id[ii_server]

    dx = xy_client[:,0] - xy_server[:,0]
    dy = xy_client[:,1] - xy_server[:,1]
    dist = (dy**2.+dx**2.)**(1./2)
    print dist
    ii_max = np.argmax (dist)
    print 'mean norm diff between poses = ', dist.mean ()
    print 'max norm diff between poses = ', dist.max ()
    
    # plot it all
    fig = plt.figure ()
    ax = fig.add_subplot (111)

    ax.plot (server_nodes.mu[:,1], server_nodes.mu[:,0], 'b-', lw=0.5)
    ax.plot (xy_server[:,1], xy_server[:,0], 'b.-', label='server', lw=2)
    for xy,cov in zip (xy_server, cov_server):
        sig = cov.reshape ((2,2))
        draw_covariance (ax, xy, sig, 9., 'b', lw=2)

    #ii = np.where (client_nodes.id > 500)[0]
    #ax.plot (client_nodes.mu[ii,1], client_nodes.mu[ii,0], 'r-')

    ax.plot (xy_client[:,1], xy_client[:,0], 'r.-', label='client', lw=1)
    for xy,cov in zip (xy_client, cov_client):
        sig = cov.reshape ((2,2))
        draw_covariance (ax, xy, sig, 9., 'r', lw=1)

    ax.legend (numpoints=1)
    ax.axis ('equal')
    ax.grid ()

    plt.show ()

    sys.exit (0)
