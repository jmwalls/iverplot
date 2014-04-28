#!/usr/bin/env python
import sys
import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lcmlog_perls import *
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=14)

class Osp_server (object):
    def __init__ (self, ser):
        utime, org_no, tol_no = [], [], []
        butime, borg_no, btol_no = [], [], []
        bbutime, bborg_no, bbtol_no = [], [], []

        for ut,org,tol in zip (ser.utime,ser.org_tol_no,ser.new_tol_no):
            if not len (utime) or ut > utime[-1]:
                utime.append (ut)
                org_no.append (org)
                tol_no.append (tol)
            elif ut==utime[-1] and tol==org_no[-1]:
                butime.append (ut)
                borg_no.append (org)
                btol_no.append (tol)
            elif ut==utime[-1] and tol==borg_no[-1]:
                bbutime.append (ut)
                bborg_no.append (org)
                bbtol_no.append (tol)

        self.utime, self.org_no, self.tol_no = np.asarray (utime), np.asarray (org_no), np.asarray (tol_no)
        self.butime, self.borg_no, self.btol_no = np.asarray (butime), np.asarray (borg_no), np.asarray (btol_no)
        self.bbutime, self.bborg_no, self.bbtol_no = np.asarray (bbutime), np.asarray (bborg_no), np.asarray (bbtol_no)

class Osp_client (object):
    def __init__ (self, ser):
        self.utime = []
        self.tol_no = []
        self.org_no = []

        for ut,org,tol in zip (ser.utime,ser.org_tol_no,ser.new_tol_no):
            if not len (self.utime) or ut > self.utime[-1]:
                self.utime.append (ut)
                self.tol_no.append (tol)
                self.org_no.append (org)

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <osp_server.pkl> <osp_client.pkl>' % sys.argv[0]
        sys.exit (0)

    with open (sys.argv[1], 'rb') as f:
        osps = pickle.load (f)
    with open (sys.argv[2], 'rb') as f:
        ospc = pickle.load (f)

    #rr = float (len (ospc.utime))/len (osps.utime)
    #print 'reception rate = %0.3f' % rr
    #bps = len (osps.utime)*64.*8./((osps.utime[-1]-osps.utime[0])*1e-6)
    #print 'average bit rate = %0.3f' % bps

    os = Osp_server (osps)
    oc = Osp_client (ospc)
    t0 = os.utime[0]

    fig = plt.figure ()
    ax = fig.add_subplot (111)

    # plot server progression
    ost = np.zeros (2*len (os.utime))
    ost[0::2] = (os.utime-t0)*1e-6
    ost[1::2] = (os.utime-t0)*1e-6
    oon = np.zeros (2*len (os.org_no))
    oon[2::2] = os.org_no[:-1]
    oon[1::2] = os.org_no
    otn = np.zeros (2*len (os.tol_no))
    otn[2::2] = os.tol_no[:-1]
    otn[1::2] = os.tol_no

    bst = np.zeros (2*len (os.butime))
    bst[0::2] = (os.butime-t0)*1e-6
    bst[1::2] = (os.butime-t0)*1e-6
    bon = np.zeros (2*len (os.borg_no))
    bon[2::2] = os.borg_no[:-1]
    bon[1::2] = os.borg_no
    btn = np.zeros (2*len (os.btol_no))
    btn[2::2] = os.btol_no[:-1]
    btn[1::2] = os.btol_no

    bbst = np.zeros (2*len (os.bbutime))
    bbst[0::2] = (os.bbutime-t0)*1e-6
    bbst[1::2] = (os.bbutime-t0)*1e-6
    bbon = np.zeros (2*len (os.bborg_no))
    bbon[2::2] = os.bborg_no[:-1]
    bbon[1::2] = os.bborg_no
    bbtn = np.zeros (2*len (os.bbtol_no))
    bbtn[2::2] = os.bbtol_no[:-1]
    bbtn[1::2] = os.bbtol_no

    ax.fill_between (bbst, bbon, bbtn, color='g', alpha=0.5)
    ax.plot (bbst, bbon, 'g', lw=2, label='2nd OSP')

    ax.fill_between (bst, bon, btn, color='b', alpha=0.5)
    ax.plot (bst, bon, 'b', lw=2, label='1st OSP')

    ax.fill_between (ost, oon, otn, color='r', alpha=0.5)
    ax.plot (ost, oon, 'r', lw=2, label='OSP')
    ax.plot (ost, otn, 'r', lw=2)
    
    # plot client progression
    ax.step ((oc.utime-t0)*1e-6, oc.tol_no, 'k', where='post', lw=4, label='Client')

    ymin,ymax = ax.get_ylim ()
    ax.set_ylim ([0, ymax])

    # find server origin shift times
    wins, wine = 3200, 4800
    ii = np.where ((np.diff (oon)!=0) & (ost[:-1] > wins) & (ost[:-1] < wine))[0]
    ax.vlines (ost[ii], oon[ii]-25, oon[ii]+25, colors='k',
            linestyle='dashed', lw=3, zorder=100)
    #for i in ii:
    #    ax.annotate ('', xy= (ost[i],otn[i]), 
    #            xytext=(ost[i], otn[i]+20),
    #            arrowprops=dict (facecolor='k',shrink=0.03,width=2,headwidth=7,frac=0.20))


    ax.axvline (wins, color='k')
    ax.axvline (wine, color='k')
    #ax.fill_betweenx ([0,ymax], [3200,3200], [4800,4800], color='k', alpha=0.15)
    #ax.text (3600,100,'NO GPS')

    ax.set_xlabel ('mission time [s]')
    ax.set_ylabel ('Server TOL index')
    
    ax.legend (loc=4)
    fig.savefig ('ladder.pdf', transparent=True, bbox_inches='tight',
            pad_inches=0)

    #figs = plt.figure ()
    #axs = figs.add_subplot (111)
    #ml,sl,bl = axs.stem ((oc.utime-t0)*1e-6, 0.1*np.ones (len (oc.utime)),
    #        basefmt='k-', linefmt='k-', markerfmt='ko')
    #plt.setp (ml, 'mfc', 'w')
    #plt.setp (ml, 'mew', 2)
    #axs.set_ylim ([0,0.15])

    plt.show ()

    sys.exit (0)
