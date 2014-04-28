#!/usr/bin/env python
"""
animate server pose-chain reconstruction
"""
import sys
import cPickle as pickle

import matplotlib.pyplot as plt

from lcmlog_perls import *
from osm_pose_chain import *

#origins = [0,8,15,22,28,34,41,47,53,60,66,73,79,85,92,98]
origins =[0]

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <server_iver.pkl> <client_iver.pkl>' % sys.argv[0]
        sys.exit (0)

    try:
        with open (sys.argv[1], 'rb') as f:
            server = pickle.load (f)
        server_osm = iver_to_osm_series (server.osm)
        with open (sys.argv[2], 'rb') as f:
            client = pickle.load (f)
        client_osm = iver_to_osm_series (client.osm)
    except Exception as err:
        print 'error loading pickles: %s' % err
        sys.exit (0)
    
    npcs = len (client_osm.pc)
    for ii_pc, client_pc in enumerate (client_osm.pc):
        # find the server pose chain that has the same last id
        for server_pc in server_osm.pc:
            if server_pc.ids[-1]==client_pc.ids[-1]: break

        sys.stdout.write ('processing %d of %d\r' % (ii_pc, npcs))
        sys.stdout.flush ()

        ii = np.in1d (server_pc.ids, client_pc.ids)
        client_xy = client_pc.xy
        server_xy = server_pc.xy[ii,:]

        dx = client_xy[:,0] - server_xy[:,0]
        dy = client_xy[:,1] - server_xy[:,1]
        dn = np.sqrt (dy**2.+dx**2.)

        fig = plt.figure (figsize=(8,10))
        ax_up = plt.subplot2grid ((3,2), (0,0), rowspan=2, colspan=2)
        ax_low = plt.subplot2grid ((3,2), (2,0), rowspan=1, colspan=2)

        ii = np.in1d (client_pc.ids, origins)
        server_pc.plot (ax_up, 'b', lw=2)
        client_pc.plot (ax_up, 'r', lw=1)
        ax_up.plot (client_xy[ii,1], client_xy[ii,0], 'yo')

        ax_up.set_xlabel ('east [m]')
        ax_up.set_ylabel ('north [m]')
        ax_up.axis ('equal')
        ax_up.grid ()

        ax_low.vlines (client_pc.ids, 0, dn, 'k')
        ax_low.plot (client_pc.ids, dn, 'bo-')
        ax_low.plot (client_pc.ids[ii], dn[ii], 'yo')

        jj = np.where (ii)[0]
        for i in jj: 
            ax_low.text (client_pc.ids[i], dn[i]+5e-11, str (client_pc.ids[i]))

        ax_low.set_ylabel ('diff [m]')
        ax_low.set_xlabel ('tol no')
        ax_low.set_xlim ([0,105])
        ax_low.set_ylim ([0,5e-10])

        fig.savefig ('osm_figs/osm%0.3d.png'%ii_pc)
        plt.close ()
    print 'finished processing...'

    sys.exit (0)
