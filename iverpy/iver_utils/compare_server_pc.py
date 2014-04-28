import sys
import cPickle as pickle

from lcmlog_perls import *
from osm_pose_chain import *

import matplotlib.pyplot as plt
#from matplotlib import rc
#rc ("text", usetex=True)
#rc ("font", family="serif")
#rc ("font", size=14)

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <server_iver.pkl> <client_iver.pkl>' % sys.argv[0]
        sys.exit (0)

    try:
        with open (sys.argv[1], 'rb') as f:
            server = pickle.load (f)
        server_osm = iver_to_osm_series (server.osm)
        with open (sys.argv[2], 'rb') as f:
            client = pickle.load (f)
        client_osm = iver_to_osm_series (client.osm)
    except Exception as err:
        print 'error loading pickles: %s' % err
        sys.exit (0)

    # let's compare the last client pose chain for now 
    client_pc = client_osm.pc[-1]
    #client_pc = client_osm.pc[-2]

    # find the server pose chain that has the same last id
    for server_pc in reversed (server_osm.pc):
        if server_pc.ids[-1]==client_pc.ids[-1]: break

    # what's the difference?
    ii = np.in1d (server_pc.ids, client_pc.ids)
    client_xy = client_pc.xy
    server_xy = server_pc.xy[ii,:]

    dx = client_xy[:,0] - server_xy[:,0]
    dy = client_xy[:,1] - server_xy[:,1]
    dist = (dy**2.+dx**2.)**(1./2)
    print dist
    ii_max = np.argmax (dist)
    print 'mean norm diff between poses = ', dist.mean ()
    print 'max norm diff between poses = ', dist.max ()
    print 'node id of max = ', client_pc.ids[ii_max]

    # plot the pose chains
    fig = plt.figure ()
    ax = fig.add_subplot (111)

    #server_pc.plot (ax, 'b', lw=2)
    #client_pc.plot (ax, 'r', lw=4)
    server_pc.plot (ax, 'b')
    client_pc.plot (ax, 'r')

    ls = ax.lines[0]
    lc = ax.lines[-1]

    ax.plot (client_xy[ii_max,1], client_xy[ii_max,0], 
            '*',mfc='y',mec='k',mew=2,label='max dist pose')

    ax.set_xlabel ('east [m]')
    ax.set_ylabel ('north [m]')

    ax.axis ('equal')
    ax.grid ()
    ax.legend ((ls, lc), ('Server', 'Client'))
    #ax.legend (numpoints=1)

    #fig.savefig ('pgreconstruct.pdf', transparent=True, bbox_inches='tight',
    #        pad_inches=0)
    plt.show ()

    sys.exit (0)
