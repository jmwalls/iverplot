import sys

import cPickle as pickle
import numpy as np
import matplotlib.pyplot as plt

from deif_lcmlog import Pose_estimate

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <est0.pkl> <est1.pkl>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        est0 = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        est1 = pickle.load (f)

    fig = plt.figure ()
    ax = fig.add_subplot (111)

    est0.plot (ax, 'b', label='first')
    est1.plot (ax, 'r', label='second')

    ax.legend ()
    ax.axis ('equal')
    ax.grid ()

    plt.show ()

    sys.exit (0)
