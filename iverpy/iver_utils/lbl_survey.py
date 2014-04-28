#!/usr/bin/env python
"""
Allow user to hand select 'good' lbl pings between a beacon and a topside ship
from an lcmlog. This is part of a post-process lbl survey pipeline that
follows the general steps on a per beacon basis:
    1. hand select 'good' pings
    2. find associated topside pose
    3. store factor
    4. optimize over topside poses and ranges to compute the lbl pose
"""

import sys

import numpy as np
from scipy.optimize import leastsq
#from scipy import sparse
#from scikits.sparse import cholmod

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from plot_utils import Picker_plot

import cPickle as pickle

import lcm
from perls import BotParam
from perls import BotCore

from lcmlog_perls import *
from isam_utils import *

speed_of_sound = 1470.

def ls_cost_func (x, xyz_b, ranges):
    """
    returns r**2 - |x-xyz_b|**2 for each beacon
    """
    r = np.zeros (ranges.shape)
    for ii, xyz in enumerate (xyz_b):
        d = np.linalg.norm (x-xyz)
        r[ii] = ranges[ii]**2 - d**2
    return r

def ls_beacon_survey (xyz, ranges):
    x,cov_x,infodict,mesg,ier = leastsq (ls_cost_func, np.array ([0,0,15]),
            args=(xyz, ranges), full_output=True)
    return x.reshape (3,1)


class Surveyor (object):
    """
    lbl surveyor object---computes beacon loations given surveyor poses and
    ranges.

    Parameters
    -----------
    nbeacons :
    owtt_utime :
    owtt :
    good_ranges :
    xyz_utime :
    xyz :
    """
    def __init__ (self, nbeacons):
        self.nbeacons = nbeacons
        self.owtt_utime = None
        self.owtt = None
        self.good_ranges = None

        self.xyz_utime = None
        self.xyz = None

        self.sol = []

    def add_poses (self, utime, lat, lon, llxy):
        """
        compute xyz from lat/lon data
        """
        y_lst, x_lst = [],[]
        for la, lo in zip (lat, lon):
            y,x = llxy.to_xy (la*180./np.pi, lo*180./np.pi)
            y_lst.append (y)
            x_lst.append (x)
        self.xyz_utime = utime
        self.xyz = np.column_stack ((x_lst, y_lst, 8.*np.ones (len (y_lst))))

    def add_ranges (self, utime, owtt, used=None):
        """
        add ranges and allow the user to reject outliers
        """
        self.owtt_utime = utime
        self.owtt = owtt[:,:self.nbeacons]
        self.good_ranges = np.zeros (self.owtt.shape)

        for ii in range (self.nbeacons):
            fig = plt.figure (figsize=(20,10))
            ax = fig.add_subplot (111)

            data = np.column_stack ((utime, owtt[:,ii]))
            if not used is None:
                jj = np.where (used[:,ii])[0]
                picker = Picker_plot (ax, data, jj)
            else:
                picker = Picker_plot (ax, data)
            plt.show ()

            jj = picker.inliers
            self.good_ranges[jj,ii] = 1
            
            kk = np.where (np.isnan (owtt[:,ii]))[0]
            self.good_ranges[kk,ii] = 0

    def solve (self):
        for ii in range (self.nbeacons):
            print '{Surveyor} solving for beacon %d position' % ii
            b_ii = np.where (self.good_ranges[:,ii])[0]

            ut = self.owtt_utime[b_ii]
            ranges = speed_of_sound * self.owtt[b_ii,ii]

            x_g = np.interp  (ut, self.xyz_utime, self.xyz[:,0])
            y_g = np.interp  (ut, self.xyz_utime, self.xyz[:,1])
            z_g = np.interp  (ut, self.xyz_utime, self.xyz[:,2])

            xyz = np.column_stack ((x_g,y_g,z_g))
            x = ls_beacon_survey (xyz, ranges)
            print x
            self.sol.append (x)
    
    def write_isam_factors (self):
        if not self.sol:
            print '{Surveyor} writing isam factors requires a prior... call solve first'
            return
        else:
            print '{Surveyor} writing isam factors to lcmlog'

        log = lcm.EventLog ('lcmlog-surveyor', 'w', overwrite=True)

        for ii in range (self.nbeacons):
            write_isam_prior3d (log, ii, self.sol[ii])

        for ii in range (len (self.owtt_utime)):
            b_ii = np.where (self.good_ranges[ii,:])[0]
            if not len (b_ii): continue

            ut = self.owtt_utime[ii]

            # write surveyor pose
            x_g = np.interp  (ut, self.xyz_utime, self.xyz[:,0])
            y_g = np.interp  (ut, self.xyz_utime, self.xyz[:,1])
            z_g = np.interp  (ut, self.xyz_utime, self.xyz[:,2])
            write_isam_prior3d (log, ut, [x_g,y_g,z_g])

            for b in b_ii:
                write_isam_range3d (log, ut, b, speed_of_sound*self.owtt[ii,b])


if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <iver.pkl> [<surveyor.pkl>]'
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        iver = pickle.load (f)

    used_ranges = None
    if len (sys.argv)==3:
        with open (sys.argv[2], 'rb') as f:
            spkl = pickle.load (f)
            used_ranges = spkl.good_ranges

    param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/topside.cfg', 'false', '')
    param = BotParam.BotParam (param_args)

    orglatlon = param.get_double_array ('site.orglatlon')
    llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])
    nbeacons = param.get_num_subkeys ('lbl.network')

    party_boat = Surveyor (nbeacons)
    party_boat.add_poses (iver.gpsd.utime, iver.gpsd.fix.latitude, iver.gpsd.fix.longitude, llxy)

    ii = np.where (iver.acomms.type==iver.acomms.NARROWBAND_LBL)[0]
    party_boat.add_ranges (iver.acomms.utime[ii], iver.acomms.owtt[ii,:],used_ranges)

    party_boat.solve ()
    party_boat.write_isam_factors ()

    #la,lo = self.llxy.to_ll (x[1], x[0])
    #print la, lo

    with open ('surveyor.pkl', 'wb') as f:
        pickle.dump (party_boat, f)

    for ii in range (party_boat.nbeacons):
        fig = plt.figure ()
        ax = fig.add_subplot (111)
        ax.plot (party_boat.xyz[:,1], party_boat.xyz[:,0], 'b')

        b = party_boat.sol[ii]
        b_ii = np.where (party_boat.good_ranges[:,ii])[0]

        ut = party_boat.owtt_utime[b_ii]
        x_g = np.interp  (ut, party_boat.xyz_utime, party_boat.xyz[:,0])
        y_g = np.interp  (ut, party_boat.xyz_utime, party_boat.xyz[:,1])
        z_g = np.interp  (ut, party_boat.xyz_utime, party_boat.xyz[:,2])

        slant_range = speed_of_sound * party_boat.owtt[b_ii,ii]
        ranges = np.sqrt (slant_range**2 - (z_g-b[2])**2  )

        for jj,r in enumerate (ranges):
            ax.add_artist (Circle ([y_g[jj],x_g[jj]], r, color='k', lw=0.5, fc='none'))

        ax.plot (b[1], b[0], '*', mfc='y', mec='k', mew=2, ms=12, 
                label='beacon '+str (ii))

        ax.legend (numpoints=1)
        ax.axis ('equal')
        ax.grid ()
    
    plt.show ()

    sys.exit (0)
