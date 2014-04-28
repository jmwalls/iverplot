#!/usr/bin/env python
import sys
import os

import cPickle as pickle

import numpy as np
import matplotlib.pyplot as plt

from lcmlog_perls import *
from osm_pose_chain import *
from centralized_filter import Centralized_solution

"""
animate origin state method in actions. creates images to produce the
following video tracks:
    1. full server pose-graph and pose-graph over server TOL states
    2. same as 1. plus client-side server reconstruction
    3. client-side reconstruction of full centralized estimator
"""

DIRFIGS = 'animationfigs'
DIRSERVER = os.path.join (DIRFIGS, 'server')
DIRCLIENT = os.path.join (DIRFIGS, 'client')
DIRSOL = os.path.join (DIRFIGS, 'sol')

class Full_graph (object):
    """
    object to hold full server pose-graph
    """
    def __init__ (self, fname):
        with open (fname, 'rb') as f:
            self.sols = pickle.load (f)

        self.index = 0
        self.len_index = len (self.sols)

    def next (self):
        if self.index < self.len_index-2:
            self.index += 1

    def tol_index (self):
        return self.sols[self.index].nodes[-1]

    def nodes (self):
        return self.sols[self.index].nodes

    def x (self):
        return self.sols[self.index].x

    def plot (self, ax, cut, *args, **kwargs):
        if not cut:
            ax.plot (self.sols[self.index].x[:,1], self.sols[self.index].x[:,0], 
                    *args, **kwargs)
        else:
            ii = np.where (self.sols[self.index].nodes > 1e5)[0]
            jj = np.where (self.sols[self.index].nodes < 1e5)[0]
            ax.plot (self.sols[self.index].x[jj,1], self.sols[self.index].x[jj,0], 
                    'r', lw=4)
            ax.plot (self.sols[self.index].x[ii,1], self.sols[self.index].x[ii,0], 
                    'b', lw=3)

class Server_graph (object):
    """
    object to hold the server pose-graph over TOL states (both server and
    client-side reconstruction)
    """
    def __init__ (self, fname):
        with open (fname, 'rb') as f:
            self.iver = pickle.load (f)
        self.osm = iver_to_osm_series (self.iver.osm)

        self.osm_index = 0
        self.len_index =  len (self.osm.pc)

    def tol_index (self):
        return self.osm.pc[self.osm_index].ids[-1]

    def next_tol_index (self):
        if self.osm_index < self.len_index-2 : ind = self.osm_index+1
        else: ind = self.osm_index
        return self.osm.pc[ind].ids[-1]

    def next (self):
        if self.osm_index < self.len_index-2: 
            self.osm_index += 1
            return True
        return False

    def plot (self, ax, *args, **kwargs):
        self.osm.pc[self.osm_index].plot (ax, *args, **kwargs)

if __name__ == '__main__':
    if len (sys.argv) < 6:
        print 'usage: %s <server_iver.pkl> <server_sols.pkl> <client_iver.pkl> <client_sols.pkl> <rnodes.pkl>' % sys.argv[0]
        sys.exit (0)

    try:
        server = Server_graph (sys.argv[1])
        client = Server_graph (sys.argv[3])
        server_full = Full_graph (sys.argv[2])
        client_full = Full_graph (sys.argv[4])

        with open (sys.argv[5], 'rb') as f:
            rnodes = pickle.load (f)
    except Exception as err:
        print 'error loading pickles: %s' % err
        sys.exit (0)

    os.mkdir (DIRFIGS)
    os.mkdir (DIRSERVER)
    os.mkdir (DIRCLIENT)
    os.mkdir (DIRSOL)

    axis = [-300,350,-300,200]
    cnt = 0
    while True:
        print 'writing new frame: %d' % cnt
        fig_server = plt.figure ()
        ax_server = fig_server.add_subplot (111)

        server_full.plot (ax_server, False, c='0.7', lw=4)
        server.plot (ax_server, 'k', lw=2)
        ax_server.axis (axis)
        ax_server.grid ()
        ax_server.set_xlabel ('North [m]')
        ax_server.set_ylabel ('East [m]')

        fig_client = plt.figure ()
        ax_client = fig_client.add_subplot (111)

        server_full.plot (ax_client, False, c='0.7', lw=4)
        server.plot (ax_client, 'k', lw=2)
        client.plot (ax_client, 'r', lw=4)
        ax_client.axis (axis)
        ax_client.grid ()
        ax_client.set_xlabel ('North [m]')
        ax_client.set_ylabel ('East [m]')

        fig_sol = plt.figure ()
        ax_sol = fig_sol.add_subplot (111)
        client_full.plot (ax_sol, True)
        nodes = client_full.nodes ()
        x = client_full.x ()
        for r in rnodes:
            ii = np.where (nodes==r[0])[0]
            jj = np.where (nodes==r[1])[0]
            if not len (ii) or not len (jj):
                continue
            xi,xj = x[ii[0],:2], x[jj[0],:2]
            ax_sol.plot ([xi[1],xj[1]], [xi[0],xj[0]], 'g', lw=2)
        ax_sol.axis (axis)
        ax_sol.grid ()
        ax_sol.set_xlabel ('North [m]')
        ax_sol.set_ylabel ('East [m]')

        if client.next_tol_index () <= server.next_tol_index ():
            client.next ()

        if server.tol_index () >= server_full.tol_index ():
            server_full.next ()

        if server.tol_index () >= client_full.tol_index ():
            client_full.next ()

        figname = 'img%03d.png' % cnt
        fig_server.savefig (os.path.join (DIRSERVER,figname),
                bbox_inches='tight', pad_inches=0)
        fig_client.savefig (os.path.join (DIRCLIENT,figname), 
                bbox_inches='tight', pad_inches=0)
        fig_sol.savefig (os.path.join (DIRSOL,figname), 
                bbox_inches='tight', pad_inches=0)

        plt.close (fig_server)
        plt.close (fig_client)
        plt.close (fig_sol)
        cnt += 1

        if not server.next (): 
            break

    sys.exit (0)
