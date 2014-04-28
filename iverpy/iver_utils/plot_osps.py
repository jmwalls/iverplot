#!/usr/bin/env python
import sys
import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lcmlog_perls import *

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog>' % sys.argv[0]
        sys.exit (0)

    if 'lcmlog' in sys.argv[1]:
        log = lcm.EventLog (sys.argv[1])
        osp = parse_from_lcm (log, "_OSP", Osp_series)
        with open ('osp.pkl', 'wb') as f:
            pickle.dump (osp, f)
    elif 'pkl' in sys.argv[1]:
        with open (sys.argv[1], 'rb') as f:
            osp = pickle.load (f)

    plt.plot (osp.utime, osp.org_tol_no, 'b')
    plt.plot (osp.utime, osp.new_tol_no, 'r')
    plt.show ()

    sys.exit (0)
