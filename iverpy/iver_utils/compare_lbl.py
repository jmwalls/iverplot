import sys
import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lbl_renav import Lbl_beacon, Lbl_fixer
from lcmlog_est import Pose_estimate

# HACK
from lcmlog_perls import *
from perls import BotParam
from perls import BotCore


if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <lbl.pkl> <est.pkl>' % sys.argv[0]
        sys.exit (0)

    # unpickle
    with open (sys.argv[1], 'rb') as f:
        lbl = pickle.load (f)

    #### BEGIN HACK TO TEST LBL V. GPS
    #with open (sys.argv[2], 'rb') as f:
    #    iver = pickle.load (f)

    #param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/iver28.cfg', 'false', '')
    #param = BotParam.BotParam (param_args)

    #orglatlon = param.get_double_array ('site.orglatlon')
    #llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])

    #xyz_utime = iver.gpsd.fix.utime
    #lat = iver.gpsd.fix.latitude
    #lon = iver.gpsd.fix.longitude
    #y_lst, x_lst = [],[]
    #for la, lo in zip (lat, lon):
    #    y,x = llxy.to_xy (la*180./np.pi, lo*180./np.pi)
    #    y_lst.append (y)
    #    x_lst.append (x)
    #xyz = np.column_stack ((x_lst, y_lst, 10.*np.ones (len (y_lst))))

    ## interpolate estimate to lbl pings
    #x_e = np.interp (lbl.sol_utime, xyz_utime, xyz[:,0])
    #y_e = np.interp (lbl.sol_utime, xyz_utime, xyz[:,1])
    #xy_e = np.vstack ((x_e,y_e))

    #### END HACK

    with open (sys.argv[2], 'rb') as f:
        est = pickle.load (f)

    # interpolate estimate to lbl pings
    x_e = np.interp (lbl.sol_utime, est.pose.utime, est.pose.xyzrph[:,0])
    y_e = np.interp (lbl.sol_utime, est.pose.utime, est.pose.xyzrph[:,1])
    xy_e = np.vstack ((x_e,y_e))

    dxy = xy_e - lbl.sol
    dx = (dxy[0,:]**2 + dxy[1,:]**2)**(1./2)

    # plot everything
    fig = plt.figure (figsize=(9,9))
    ax = fig.add_subplot (111)
    
    ax.plot (lbl.sol[1,:], lbl.sol[0,:], 'bo-', label='LBL')
    ax.plot (xy_e[1,:], xy_e[0,:], 'r.-', label='estimate')
    #est.plot (ax, 'r')

    ax.set_xlabel ('east [m]')
    ax.set_ylabel ('north [m]')

    ax.legend ()
    ax.axis ('equal')
    ax.grid ()

    fig_comp = plt.figure (figsize=(15,9))
    ax_comp = fig_comp.add_subplot (111)

    ax_comp.plot ((lbl.sol_utime-lbl.sol_utime[0])*1e-6, dx, '.-')

    ax_comp.set_xlabel ('mission time [s]')
    ax_comp.set_ylabel ('LBL error [m]')

    #fig_hist = plt.figure ()
    #ax_hist = fig_hist.add_subplot (111)

    #ax_hist.plot (dxy[0,:], dxy[1,:], 'g.')
    #ax_hist.axis ('equal')
    #ax_hist.grid ()

    plt.show ()

    sys.exit (0)
