import sys

import matplotlib.pyplot as plt

import lcm
from lcmlog_perls import *


if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-isam>' % sys.argv[0]
        sys.exit (0)

    log = lcm.EventLog (sys.argv[1])
    nodes = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)

    print 'found %d nodes' % (len (nodes.id))

    #ii_client = np.where (nodes.id%10==2)[0]
    ii_client = np.where (nodes.id > 10e5)[0]
    plt.plot (nodes.mu[ii_client,1], nodes.mu[ii_client,0], 'b.-')

    #ii_server = np.where (nodes.id%10==3)[0]
    ii_server = np.where (nodes.id < 10e5)[0]
    plt.plot (nodes.mu[ii_server,1], nodes.mu[ii_server,0], 'r.-')

    #plt.plot (nodes.mu[:,1], nodes.mu[:,0], 'k.')

    plt.axis ('equal')
    plt.grid ()

    plt.show ()

    sys.exit (0)
