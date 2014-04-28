#!/usr/bin/env python
import sys
import cPickle as pickle

import numpy as np

from lcmlog_perls import *
from perls import BotParam
from perls import BotCore

import matplotlib.pyplot as plt
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=18)
#rc ("font", size=14)

if __name__ == '__main__':
    if len (sys.argv) < 4:
        print 'usage: %s <iver31.pkl> <iver28.pkl> <iver_topside.pkl>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        iver31 = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        iver28 = pickle.load (f)
    with open (sys.argv[3], 'rb') as f:
        topside = pickle.load (f)

    param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/iver28.cfg', 'false', '')
    param = BotParam.BotParam (param_args)
    orglatlon = param.get_double_array ('site.orglatlon')
    llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])

    ## find lbl beacons
    #nbeacons, x_lbl, y_lbl = param.get_num_subkeys ('lbl.network'), [], []
    #for ii in range (nbeacons):
    #    latlon = param.get_double_array ('lbl.network.beacon%d.latlon'%ii)
    #    y,x = llxy.to_xy (latlon[0], latlon[1])
    #    x_lbl.append (x)
    #    y_lbl.append (y)

    xy_iver31 = iver31.state.position.xyzrph[:,:2]
    xy_iver28 = iver28.state.position.xyzrph[:,:2]

    lat = topside.gpsd.fix.latitude
    lon = topside.gpsd.fix.longitude
    y_lst, x_lst = [],[]
    for la, lo in zip (lat, lon):
        y,x = llxy.to_xy (la*180./np.pi, lo*180./np.pi)
        y_lst.append (y)
        x_lst.append (x)
    xy_topside = np.column_stack ((x_lst, y_lst))

    fig = plt.figure ()
    ax = fig.add_subplot (111)

    ax.plot (xy_iver31[:,1], xy_iver31[:,0], 'b', lw=4, label='AUV1')
    ax.plot (xy_iver28[:,1], xy_iver28[:,0], 'r', lw=3, label='AUV2')
    ax.plot (xy_topside[:,1], xy_topside[:,0], c='0.3', lw=2, label='Topside')

    #l1 = ax.legend (numpoints=1, loc=1)

    s1, = ax.plot (xy_iver31[0,1], xy_iver31[0,0], 'D', ms=12, mfc='k', mew=3, mec='k')
    e1, = ax.plot (xy_iver31[-1,1], xy_iver31[-1,0], 's', ms=15, mfc='k', mew=3, mec='k')
    s2, = ax.plot (xy_iver28[0,1], xy_iver28[0,0], 'D', ms=12, mfc='w', mew=3, mec='k')
    e2, = ax.plot (xy_iver28[-1,1], xy_iver28[-1,0], 's', ms=15, mfc='w', mew=3, mec='k')
    #l2 = ax.legend ([s1,e1,s2,e2], ['AUV1 Start', 'AUV1 End', 'AUV2 Start',
    #    'AUV2 End'], numpoints=1, loc=8, ncol=2)
    #ax.add_artist (l1)

    #ax.plot (y_lbl, x_lbl, '*', ms=30, mfc='y', mec='k', mew=4, label='LBL Beacons')

    ax.axis ('equal')
    #ax.set_xlim ([-250,450]) # for legend 8/18
    #ax.set_ylim ([-450,250])
    #ax.set_xlim ([-275,500]) # for lbl setup
    #ax.set_ylim ([-315,275])
    ax.grid ()
    ax.set_xlabel ('East [m]')
    ax.set_ylabel ('North [m]')

    fig.savefig ('trial.pdf', transparent=True, bbox_inches='tight',
            pad_inches=0)

    plt.show ()

    sys.exit (0)
