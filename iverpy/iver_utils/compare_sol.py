import sys

import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt

from centralized_filter import Centralized_solution

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <sol0.pkl> <sol1.pkl>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        sol0 = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        sol1 = pickle.load (f)

    # find client nodes
    #ii = np.where ((sol0.nodes < 1e5) & (sol0.nodes > 1e4))[0] # server tol nodes
    #ii = np.where (sol0.nodes < 1e4)[0] # server tol nodes
    #ii = np.where (sol0.nodes < 1e5)[0] # server tol nodes
    ii = np.where (sol0.nodes > 1e5)[0] # client nodes
    nodes = sol0.nodes[ii]

    ii = np.in1d (sol1.nodes, nodes)
    nodes = sol1.nodes[ii]

    # sol0 xy
    ii = np.in1d (sol0.nodes, nodes)
    xy0 = sol0.x[ii,:]

    # sol1 xy
    ii = np.in1d (sol1.nodes, nodes)
    xy1 = sol1.x[ii,:]

    # compute difference
    dxy = xy0-xy1
    ndxy = np.sqrt (dxy[:,0]**2 + dxy[:,1]**2)

    print 'mean norm diff between poses = ', ndxy.mean ()
    print 'max norm diff between poses = ', ndxy.max ()

    # plot everything
    fig = plt.figure (figsize=(8,10))
    ax_path = plt.subplot2grid ((3,2), (0,0), rowspan=2, colspan=2)
    ax_diff = plt.subplot2grid ((3,2), (2,0), rowspan=1, colspan=2)
    
    ax_path.plot (xy0[:,1], xy0[:,0], 'b.-', label='first', lw=2)
    ax_path.plot (xy1[:,1], xy1[:,0], 'r.-', label='second')

    ax_path.legend ()
    ax_path.axis ('equal')
    ax_path.grid ()

    t = (nodes-nodes[0])*1e-6
    ax_diff.plot (t, ndxy, 'b')

    #jj = np.argmin (np.abs (sol0.nodes-27)) #iver28 dive001 08-19
    ##jj = np.argmin (np.abs (sol0.nodes-14)) #topside dive001 08-19
    #jj = np.where (nodes==sol0.nodes[jj+1])[0]
    #ax_diff.axvline (t[jj], c='k', lw=2)

    ax_diff.set_xlabel ('mission time [s]')

    plt.show ()

    sys.exit (0)
