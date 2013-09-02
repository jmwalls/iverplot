"""
Compute lbl fixes from iver lcmlogs following the general processing pipeline

for each narrowband lbl range:
    * reject outliers (median filter?)
    * compute fix
        * 2-beacon fix, use iver xy to choose solution
        * M-beacon ls fix

This is a post-process lbl pipeline. The goal is to compute *good* lbl fixes
given the data. As such, we do not need to compute fixes within a filtering
framework and can consider all the data at once. Here, we perform an automated
outlier rejection based on a median filter and also allow the user to reject
outliers before computing a fix.
"""

import numpy as np
from scipy.signal import medfilt
from scipy.optimize import leastsq

from plot_utils import Picker_plot

speed_of_sound = 1470.

MEDIAN_THRESHOLD = 45./speed_of_sound
MEDIAN_WIN_SIZE = 5

MAX_DIST_THRESHOLD = 15.

class Lbl_beacon (object):
    """
    lbl beacon object contains the beacon id, position, and median filter
    """
    def __init__ (self, ind, xyz, win_size=3, med_threshold=150):
        print '{Lbl_beacon} created beacon %d at position = %0.3f,%0.3f,%0.3f' % (ind,xyz[0],xyz[1],xyz[2])
        self.index = ind
        self.xyz = xyz


def two_beacon_fix (b0, r0, b1, r1, xy_guess):
    """
    compute lbl fix given two range circles

    Parameters
    -----------
    b0/1 : Lbl_beacon object
    r0/1 : owtt derived ranges
    xy_guess : position guess to disambiguate which side of the baseline
    """
    x0 = b0.xyz[:2].reshape (2,1)
    x1 = b1.xyz[:2].reshape (2,1)

    dx = x1-x0
    D = np.linalg.norm (dx)
    if r0 + r1 < D: return None

    t = (r0**2 - r1**2 + D**2)/(2*D**2)
    xl = x0 + t*dx

    l0 = np.linalg.norm (xl-x0)
    h = (r0**2 - l0**2)**(1./2)
    n = np.array ([[-dx[1,0]],[dx[0,0]]])/D

    xp0 = xl + h*n
    xp1 = xl - h*n

    d0 = np.linalg.norm (xp0-xy_guess)
    d1 = np.linalg.norm (xp1-xy_guess)

    # MAX_DIST_THRESHOLD is a little hacky...
    if d0 > MAX_DIST_THRESHOLD and d1 > MAX_DIST_THRESHOLD: return None
    elif d0 < d1: return xp0
    else: return xp1


def ls_cost_func (x, beacons, ranges):
    """
    returns r**2 - (x-b.x)**2 for each beacon
    """
    r = np.zeros (len (beacons))
    for ii, b in enumerate (beacons):
        d = np.linalg.norm (x-b.xyz[:2])
        r[ii] = ranges[ii]**2 - d**2
    return r

def ls_beacon_fix (beacons, ranges, xy_guess):
    """
    compute lbl fix given M range circles

    Parameters
    -----------
    beacons :
    ranges :
    xy_guess : position guess to seed optimization
    """
    x,success = leastsq (ls_cost_func, xy_guess.reshape (2), args=(beacons, ranges))

    if not success: return None
    #elif np.linalg.norm (x-xy_guess) > MAX_DIST_THRESHOLD: return None
    else: return x.reshape (2,1)


class Lbl_fixer (object):
    """
    lbl localization object---computes position fixes given beacon locations
    and ranges.

    The general processing pipeline involves 
    * pushing all ranging interrogations
    * automated outlier rejection
    * manual outlier rejection
    * computing fixes

    Parameters
    -----------
    beacons : list of M lbl beacon objects

    utime : N array_like of ranging utimes
    owtts : NxM array_like of owtt ranges
    beacons_used : NxM array_like indicating whether a beacons was used for a fix

    sol : Nx2 array_like of xy position fixes, Nan if not enough ranges are
        available
    """
    def __init__ (self, beacons, utime, owtts, used=None):
        """
        constructor

        Parameters
        -----------
        beacons : beacon objects
        utime :
        owtts :
        used : NxM array indicated indices of 'good' beacon observations
        """
        self.beacons = beacons

        self.utime = utime
        self.owtts = owtts

        # median filter beacons
        self.beacons_used = np.zeros (owtts.shape)
        for ii in range (len (beacons)):
            owtt = owtts[:,ii]

            #owtt_median = medfilt (owtt, kernel_size=MEDIAN_WIN_SIZE)
            #diff = np.abs (owtt_median-owtt)
            #jj = np.argwhere (diff < MEDIAN_THRESHOLD)

            fig = plt.figure (figsize=(20,10))
            ax = fig.add_subplot (111)

            data = np.vstack ((self.utime, owtt)).T
            if not used is None: 
                jj = np.where (used[:,ii])[0]
                picker = Picker_plot (ax, data, jj)
            else: 
                picker = Picker_plot (ax, data)

            plt.show ()

            jj = picker.inliers
            self.beacons_used[jj,ii] = 1

            kk = np.where (np.isnan (owtt))[0]
            self.beacons_used[kk,ii] = 0

        self.sol = None
        self.sol_utime = None

    def solve (self, xy_utime, xy):
        """
        compute lbl fixes.
        """
        print '{Lbl_fixer} solving...'
        good_beacons = self.beacons_used.sum (axis=1)
        print '0 beacon fixes:', np.count_nonzero (good_beacons==0)
        print '1 beacon fixes:', np.count_nonzero (good_beacons==1)
        print '2 beacon fixes:', np.count_nonzero (good_beacons==2)
        print '3 beacon fixes:', np.count_nonzero (good_beacons==3)
        
        sol = []
        utime = []
        for ii in range (len (self.utime)):
            b_ii = np.where (self.beacons_used[ii,:])[0]

            ut = self.utime[ii]
            x_g = np.interp (ut, xy_utime, xy[:,0])
            y_g = np.interp (ut, xy_utime, xy[:,1])
            z_g = np.interp (ut, xy_utime, xy[:,2])
            xy_g = np.array ([[x_g],[y_g]])

            if len (b_ii) == 2:
                b0 = self.beacons[b_ii[0]]
                b1 = self.beacons[b_ii[1]]

                z0 = ((speed_of_sound*self.owtts[ii,b_ii[0]])**2 - (z_g-b0.xyz[2])**2)**(1./2)
                z1 = ((speed_of_sound*self.owtts[ii,b_ii[1]])**2 - (z_g-b1.xyz[2])**2)**(1./2)

                pos = two_beacon_fix (b0, z0, b1, z1, xy_g) 
                if not pos is None: 
                    sol.append (pos)
                    utime.append (ut)

            elif len (b_ii) > 2:
                beacons, ranges = [], []
                for jj in range (nbeacons):
                    if not jj in b_ii: continue
                    b = self.beacons[jj]
                    pr = speed_of_sound*self.owtts[ii,jj] 
                    r = (pr**2 - (z_g-b.xyz[2])**2)**(1./2)
                    beacons.append (b)
                    ranges.append (r)

                pos = ls_beacon_fix (beacons, ranges, xy_g)
                if not pos is None: 
                    sol.append (pos)
                    utime.append (ut)

        self.sol = np.asarray (sol).reshape (len (sol), 2).T
        self.sol_utime = np.asarray (utime)


if __name__ == '__main__':
    import sys

    import cPickle as pickle
    import matplotlib.pyplot as plt

    import lcm
    from perls import BotParam
    from perls import BotCore

    from perls_lcmlog import *

    # load iver data
    if len (sys.argv) < 2:
        print 'usage: %s <iver.pkl>' % sys.argv[0]
        sys.exit (0)

    if len (sys.argv) == 3:
        with open (sys.argv[2], 'rb') as f:
            fix_pkl = pickle.load (f)
    else:
        fix_pkl = None

    with open (sys.argv[1], 'rb') as f:
        iver = pickle.load (f)


    # load params
    param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/iver28.cfg', 'false', '')
    param = BotParam.BotParam (param_args)

    orglatlon = param.get_double_array ('site.orglatlon')
    llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])

    # initialize lbl beacons
    nbeacons, beacons = param.get_num_subkeys ('lbl.network'), []
    for ii in range (nbeacons):
        latlon = param.get_double_array ('lbl.network.beacon%d.latlon'%ii)
        y,x = llxy.to_xy (latlon[0], latlon[1])
        z = param.get_double ('lbl.network.beacon%d.depth'%ii)
        xyz = np.array ([x,y,z])
        beacons.append (Lbl_beacon (ii, xyz))

    ii_lbl = np.where (iver.acomms.type==iver.acomms.NARROWBAND_LBL)[0]
    
    if not fix_pkl is None:
        fix = Lbl_fixer (beacons, 
                iver.acomms.utime[ii_lbl], iver.acomms.owtt[ii_lbl,:nbeacons],
                fix_pkl.beacons_used) 
    else:
        fix = Lbl_fixer (beacons, 
                iver.acomms.utime[ii_lbl], iver.acomms.owtt[ii_lbl,:nbeacons]) 
    fix.solve (iver.state.position.utime, iver.state.position.xyzrph[:,:3])

    with open ('lbl_fixer.pkl', 'wb') as f:
        pickle.dump (fix, f)

    # plot median filter and position fix results
    fig0 = plt.figure ()

    for ii,b in enumerate (beacons):
        is_good = np.asarray (fix.beacons_used[:,ii])
        ii_g = np.where (is_good==1)[0] 
        ii_b = np.where (is_good==0)[0]
        ut = np.asarray (fix.utime)
        owtt = fix.owtts[:,ii]

        ax = fig0.add_subplot (3,1,ii)
        ax.plot (ut[ii_g],owtt[ii_g],'o',mfc='w',mec='b')
        ax.plot (ut[ii_b],owtt[ii_b],'rx',mew=3)

    fig1 = plt.figure ()
    ax1 = fig1.add_subplot (111)

    ax1.plot (iver.state.position.xyzrph[:,1], iver.state.position.xyzrph[:,0], 'r')
    ax1.plot (fix.sol[1,:], fix.sol[0,:], 'bo-')
    for b in beacons:
        ax1.plot (b.xyz[1], b.xyz[0], '*', mfc='y', mec='k', ms=15, mew=3)
    ax1.axis ('equal')
    ax1.grid ()

    plt.show ()

    sys.exit (0)
