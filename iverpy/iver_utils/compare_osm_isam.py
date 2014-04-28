import sys
import cPickle as pickle

import matplotlib.pyplot as plt

import lcm
from lcmlog_perls import *
from osm_pose_chain import *

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <client_iver.pkl> <lcmlog-isam>' % sys.argv[0]
        sys.exit (0)

    try:
        with open (sys.argv[1], 'rb') as f:
            client = pickle.load (f)
        client_eif = iver_to_osm_series (client.osm)

        log = lcm.EventLog (sys.argv[2])
        isam_nodes = parse_from_lcm (log, 'ISAM_NODES', Isam_node_series)
        client_isam = isam_to_osm_series (isam_nodes)
    except Exception as err:
        print 'error loading logs: %s' % err
        sys.exit (0)

    pc_eif = client_eif.pc[-1]
    pc_isam = client_isam.pc[-1]

    # what's the difference
    xy_eif = pc_eif.xy

    ii = np.in1d (pc_isam.ids, pc_eif.ids)
    xy_isam = pc_isam.xy[ii,:]
    cov_isam = pc_isam.cov[ii,:]

    dx = xy_eif[:,0] - xy_isam[:,0]
    dy = xy_eif[:,1] - xy_isam[:,1]
    dist = (dy**2.+dx**2.)**(1./2)
    print dist
    ii_max = np.argmax (dist)
    print 'mean norm diff between poses = ', dist.mean ()
    print 'max norm diff between poses = ', dist.max ()

    # plot the pose chains
    fig = plt.figure ()
    ax = fig.add_subplot (111)

    pc_eif.plot (ax, 'b', lw=2)

    for xy,cov in zip (xy_isam, cov_isam):
        sig = cov.reshape ((2,2))
        draw_covariance (ax, xy, sig, 9., 'r', lw=1)
    ax.plot (xy_isam[:,1], xy_isam[:,0], 'r.-', lw=1)
    #pc_isam.plot (ax, 'r', lw=1)

    ax.plot (xy_eif[ii_max,1], xy_eif[ii_max,0], 
            '*',mfc='y',mec='k',mew=2,label='max dist pose')

    ax.axis ('equal')
    ax.grid ()
    ax.legend (numpoints=1)

    plt.show ()

    sys.exit (0)
