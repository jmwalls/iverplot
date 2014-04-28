#!/usr/bin/env python
"""
plot information matrix and vector
"""
import sys

import numpy as np
from scipy.linalg import cho_factor, cho_solve
import matplotlib.pyplot as plt

import lcm
from perls.lcmtypes.perllcm import iver_osm_test_t

def marginalize (L, e, inds):
    if not len (inds): return L,e

    inds = np.asarray (inds)
    ii = np.sort (np.hstack ((2*inds, 2*inds+1)))
    jj = np.setdiff1d (np.arange (len (e)), ii)

    Laa = L[jj,:][:,jj]
    Lbb = L[ii,:][:,ii]
    Lab = L[jj,:][:,ii]

    ea = e[jj]
    eb = e[ii]

    chc,chl = cho_factor (Lbb)
    Lbb_inv = cho_solve ((chc,chl),np.eye (Lbb.shape[0]))

    Lm = Laa - Lab.dot (Lbb_inv.dot (Lab.T))
    em = ea - Lab.dot (Lbb_inv.dot (eb))

    return Lm,em

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-server> <lcmlog-client>' % sys.argv[0]
        sys.exit (0)

    logs = lcm.EventLog (sys.argv[1])
    osms = [iver_osm_test_t.decode (e.data) for e in logs if e.channel=='OSM_TEST']

    logc = lcm.EventLog (sys.argv[2])
    osmc = [iver_osm_test_t.decode (e.data) for e in logc if e.channel=='OSM_TEST']


    for ii,oc in enumerate (osmc):
        #sys.stdout.write ('processing %d of %d\r' % (ii,len (osmc)))
        #sys.stdout.flush ()

        Lc = np.asarray (oc.Lambda).reshape (oc.n,oc.n)
        ec = np.asarray (oc.eta).reshape (oc.n,1)

        for os in osms:
            if os.index[-1]==oc.index[-1]: break

        Ls = np.asarray (os.Lambda).reshape (os.n,os.n)
        es = np.asarray (os.eta).reshape (os.n,1)

        # marginalize out other nodes
        jj = np.setdiff1d (os.index, oc.index)
        Lsm,esm = marginalize (Ls,es,jj)

        dL = Lc-Lsm
        de = ec-esm
    
        figL = plt.figure (figsize=(7,7))
        axL = figL.add_subplot (111)
        imL = axL.imshow (dL, interpolation='none')
        figL.colorbar (imL)
        axL.axis ('off')

        fige = plt.figure (figsize=(2,7)) 
        axe = fige.add_subplot (111)
        ime = axe.imshow (de, interpolation='none')
        fige.colorbar (ime)
        axe.axis ('off')

        plt.show ()
        plt.close ()

        if ii==5: sys.exit (0)
    print 'finished processing...'

    sys.exit (0)
