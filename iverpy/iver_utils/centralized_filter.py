#!/usr/bin/env python
import sys
from time import gmtime

import numpy as np

from scipy import sparse
from scikits.sparse import cholmod

import matplotlib.pyplot as plt
from plot_utils import draw_covariance

import lcm
from perls.lcmtypes.perllcm import isam2_f_glc_t
from perls.lcmtypes.perllcm import isam2_f_prior_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_partial_t
from perls.lcmtypes.perllcm import position_t

class Centralized (object):
    """
    Centralized information filter object for post-processing a set of factors
    (from separate vehicles) and computing the joint posterior over trajetory
    poses.

    The filter tracks the nonzero entries of the full information
    matrix/vector and then populates a scipy sparse coo_matrix when called on
    to 'solve'. The cholmod package is used to efficiently compute the
    resulting linear system.

    Parameters
    -----------
    utime : current filter utime
    nodes : list of node ids
    index : dictionary of node id to information matrix/vector index

    _Ns : size of single state
    
    _rows : list nonzero rows of entries of the information matrix
    _cols : list nonzero cols of entries of the information matrix
    _data : list nonzero entries of the information matrix

    _vector : list nonzero entries of information vector

    nlogs : number of logs (platforms)
    lcmlogs : list of lcmlog for each vehicle, we assume the 'client' is
        always the first log
    ids : map from log id to node indices
    events : next event from each log
    """
    def __init__ (self, logs):
        self.sols, self.rnodes = [], []
        self.utime = None

        self.nodes = []
        self.index = {}
        self.node_utime = []

        self._Ns = 2

        self._rows, self._cols, self._data = [],[],[]
        self._vector = []

        self.x = None
        self.cov = None

        self.nlogs = len (logs)
        self.lcmlogs = logs

        # find server node ids for range events---client log is 0th
        rfactors = [isam2_f_pose_pose_partial_t.decode (e.data) for e in logs[0] if e.channel=='F_RANGE2D']
        #rfactors = [isam2_f_glc_t.decode (e.data) for e in logs[0] if e.channel=='F_DS2D']
        logs[0].seek (0)
        self.range_ids = [f.node_id2 for f in rfactors]
        #self.range_ids = [f.node_id[1] for f in rfactors]
        self.rid = 0

        self.ids = {ii:[] for ii in range (self.nlogs)}
        self.events = [l.read_next_event () for l in self.lcmlogs]
        self.lid = self.nlogs-1 # active log id

    def solve (self, recover_cov=False):
        n = len (self.nodes)
        L = sparse.coo_matrix ((self._data, (self._rows,self._cols)), 
                shape=(self._Ns*n,self._Ns*n))
        e = np.asarray (self._vector)
        factor = cholmod.cholesky (L.tocsc ())

        x = factor (e)
        self.x = x.reshape (n,self._Ns)

        if recover_cov:
            S = factor (np.eye (self._Ns*n))
            Smarginal = [S[ii:ii+2,ii:ii+2].ravel ().tolist () for ii in range (0,self._Ns*n,self._Ns)]
            self.cov = np.asarray (Smarginal)
        else: self.cov = np.zeros ((n,4))

    def publish (self, log):
        return
        if self.utime is None: return
        if not self.utime in self.index: return

        self.solve (recover_cov=False)
        ii = self.index[self.utime]/self._Ns
        #ii = len (self.nodes)-1 # hack to publish server
        pose = position_t ()    
        pose.utime = self.utime
        pose.xyzrph[0] = self.x[ii,0];
        pose.xyzrph[1] = self.x[ii,1];
        pose.xyzrph_cov[0] = self.cov[ii,0];
        pose.xyzrph_cov[1] = self.cov[ii,1];
        pose.xyzrph_cov[6] = self.cov[ii,2];
        pose.xyzrph_cov[7] = self.cov[ii,3];
        log.write_event (self.utime, 'CLIENT_FILTER_TEST', pose.encode ())

    def add_node (self, node_id, utime, li):
        print '{Centralized} adding node %d, id %d' % (len (self.nodes),node_id)
        self.ids[li].append (len (self.nodes))
        self.index[node_id] = self._Ns*len (self.nodes)

        self.nodes.append (node_id)
        self.node_utime.append (utime)

        self._vector.extend ([0.]*self._Ns)

    def add_prior_factor (self, f, li):
        #if f.node_id > 1e5: return # temp hack
        if not f.node_id in self.nodes:
            self.add_node (f.node_id, f.utime, li)

        S = np.asarray (f.R).reshape (self._Ns,self._Ns)
        L = np.linalg.inv (S)
        e = L.dot (f.z)
        
        ii = self.index[f.node_id]
        for r in range (self._Ns):
            self._vector[ii+r] += e[r]
            for c in range (f.n):
                self._rows.append (ii+r)
                self._cols.append (ii+c)
                self._data.append (L[r,c])

    def add_odo_factor (self, f, li):
        #if f.node_id1 > 1e5: return # temp hack
        if not f.node_id1 in self.nodes:
            raise Exception ('Odometry factor expects initialized node_id1!')
        if not f.node_id2 in self.nodes:
            self.add_node (f.node_id2, f.utime, li)

        S = np.asarray (f.R).reshape (self._Ns, self._Ns)
        L = np.linalg.inv (S)
        e = L.dot (f.z)

        ii = self.index[f.node_id1]
        jj = self.index[f.node_id2]
        for r in range (self._Ns):
            self._vector[ii+r] += -e[r]
            self._vector[jj+r] += e[r]
            for c in range (self._Ns):
                # node 1 elements
                self._rows.append (ii+r)
                self._cols.append (ii+c)
                self._data.append (L[r,c])

                # node 2 elements
                self._rows.append (jj+r)
                self._cols.append (jj+c)
                self._data.append (L[r,c])

                # off diagonal elements
                self._rows.append (ii+r)
                self._cols.append (jj+c)
                self._data.append (-L[r,c])
                self._rows.append (jj+r)
                self._cols.append (ii+c)
                self._data.append (-L[r,c])

    def add_range_factor (self, f):
        if not f.node_id1 in self.nodes or not f.node_id2 in self.nodes:
            print f.node_id1, f.node_id2
            raise Exception ('Range factor expects initialized node_id1/2!')

        ii = self.index[f.node_id1]
        jj = self.index[f.node_id2]
        
        self.solve ()
        xi = self.x[ii/self._Ns,:]
        xj = self.x[jj/self._Ns,:]

        x = np.hstack ((xi,xj))
        dx = (xi-xj).reshape (2,1)
        z_pred = np.linalg.norm (dx)

        Ji = (np.dot (dx.T, dx)**(-0.5))*dx.T
        Jj = -(np.dot (dx.T, dx)**(-0.5))*dx.T
        J = np.hstack ((Ji,Jj))

        L = (1./f.R[0])*J.T.dot (J)
        e = (1./f.R[0])*J.T.dot (f.z - (z_pred-J.dot (x)))

        for r in range (self._Ns):
            self._vector[ii+r] += e[r]
            self._vector[jj+r] += e[self._Ns+r]
            for c in range (self._Ns):
                # node 1 elements
                self._rows.append (ii+r)
                self._cols.append (ii+c)
                self._data.append (L[r,c])

                # node 2 elements
                self._rows.append (jj+r)
                self._cols.append (jj+c)
                self._data.append (L[self._Ns+r,self._Ns+c])

                # off diagonal elements
                self._rows.append (ii+r)
                self._cols.append (jj+c)
                self._data.append (L[r,self._Ns+c])
                self._rows.append (jj+r)
                self._cols.append (ii+c)
                self._data.append (L[self._Ns+r,c])

    #def add_glc_factor (self, f):
    #    node_id1,node_id2 = f.node_id[0], f.node_id[1]
    #    if not node_id1 in self.nodes or not node_id2 in self.nodes:
    #        raise Exception ('Range factor expects initialized node_id1/2!')
    #    x = np.asarray (f.x).reshape (4)
    #    G = np.asarray (f.G).reshape (4,4)
    #    L = G.T.dot (G)
    #    e = G.T.dot (G.dot (x))
    #    ii = self.index[node_id1]
    #    jj = self.index[node_id2]
    #    for r in range (self._Ns):
    #        self._vector[ii+r] += e[r]
    #        self._vector[jj+r] += e[self._Ns+r]
    #        for c in range (self._Ns):
    #            # node 1 elements
    #            self._rows.append (ii+r)
    #            self._cols.append (ii+c)
    #            self._data.append (L[r,c])
    #            # node 2 elements
    #            self._rows.append (jj+r)
    #            self._cols.append (jj+c)
    #            self._data.append (L[self._Ns+r,self._Ns+c])
    #            # off diagonal elements
    #            self._rows.append (ii+r)
    #            self._cols.append (jj+c)
    #            self._data.append (L[r,self._Ns+c])
    #            self._rows.append (jj+r)
    #            self._cols.append (ii+c)
    #            self._data.append (L[self._Ns+r,c])

    def add_ds_factor (self, f, li):
        node_id1,node_id2 = f.node_id[0], f.node_id[1]
        if not node_id1 in self.nodes:
            self.add_node (node_id1, f.utime, li)
        if not node_id2 in self.nodes:
            self.add_node (node_id2, f.utime, li)

        de = np.asarray (f.x).reshape (4)
        dL = np.asarray (f.G).reshape (4,4)

        ii = self.index[node_id1]
        jj = self.index[node_id2]
        for r in range (self._Ns):
            self._vector[ii+r] += de[r]
            self._vector[jj+r] += de[self._Ns+r]
            for c in range (self._Ns):
                # node 1 elements
                self._rows.append (ii+r)
                self._cols.append (ii+c)
                self._data.append (dL[r,c])

                # node 2 elements
                self._rows.append (jj+r)
                self._cols.append (jj+c)
                self._data.append (dL[self._Ns+r,self._Ns+c])

                # off diagonal elements
                self._rows.append (ii+r)
                self._cols.append (jj+c)
                self._data.append (dL[r,self._Ns+c])
                self._rows.append (jj+r)
                self._cols.append (ii+c)
                self._data.append (dL[self._Ns+r,c])

    def next_event (self):
        """
        first return all events in server log up until next tol, then return
        all client events through range measurement.
        """
        #utime = [e.timestamp for e in self.events]
        ##ii = np.argmin (utime)
        #iisort = np.argsort (utime)
        ##not1,not2 = False,False
        ##if 1103 in self.nodes:
        ##    not1 = True
        ##    print 'finished 28'
        ##if 10094 in self.nodes:
        ##    not2 = True
        ##    print 'finished 31'
        #ii = iisort[0]
        ##if ii==1 and not1:
        ##    if not2:
        ##        ii = 0
        ##    else:
        ##        ii = iisort[1]
        ##if ii==2 and not2:
        ##    if not1:
        ##        ii = 0
        ##    else:
        ##        ii = iisort[1]

        #e = self.events[ii]
        #ne = self.lcmlogs[ii].read_next_event ()
        #while not ne is None and (ne.channel=='REQUEST_STATE' or ne.channel=='CMD'):
        #    ne = self.lcmlogs[ii].read_next_event ()

        #self.events[ii] = ne
        #if not ne is None: return ii,e
        #else: return 0,None
        
        ii = self.lid
        e = self.events[ii]
        ne = self.lcmlogs[ii].read_next_event ()
        while not ne is None and (ne.channel=='REQUEST_STATE' or ne.channel=='CMD'):
            ne = self.lcmlogs[ii].read_next_event ()
        self.events[ii] = ne

        if e is None: return 0,e
        #if self.rid > len (self.range_ids)-1: return 0,None
        if self.lid==0:
            if e.channel=='F_RANGE2D':
                f = isam2_f_pose_pose_partial_t.decode (e.data)
                if f.node_id2==self.range_ids[self.rid]:
                    self.rid+=1
                    self.lid=self.nlogs-1
        else:
            if e.channel=='F_PRIOR2D':
                f = isam2_f_prior_t.decode (e.data)
                if f.node_id==self.range_ids[self.rid]:
                    self.lid=0
            elif e.channel=='F_ODO2D':
                f = isam2_f_pose_pose_t.decode (e.data)
                if f.node_id2==self.range_ids[self.rid]:
                    self.lid=0
        return ii, e

    def run (self, log):
        """
        basic idea is to process all other logs up to the next tol node id,
        then process client through the range measurement, then lather rinse
        and repeat until all range measurements have been reached.
        """
        if self.nlogs==1: logname = 'lcmlog-decentralized'
        else: logname = 'lcmlog-centralized'
        est_log = lcm.EventLog (logname, 'w', overwrite=True)

        li,e = self.next_event ()
        while not e is None:
            if e.channel=='F_PRIOR2D':
                f = isam2_f_prior_t.decode (e.data)
                self.add_prior_factor (f,li)
                if li==0 and f.utime > self.utime and f.node_id > 1e5: 
                    self.publish (est_log)
                    self.utime = f.utime
            elif e.channel=='F_ODO2D':
                f = isam2_f_pose_pose_t.decode (e.data)
                self.add_odo_factor (f,li)
                if li==0 and f.utime > self.utime and f.node_id1 > 1e5: 
                    self.publish (est_log)
                    self.utime = f.utime
                #if li==0 and f.node_id2 < 1e5:
                #    self.solve ()
                #    sol = Centralized_solution (self.ids, self.nodes, self.x, self.cov)
                #    self.sols.append (sol)
            elif e.channel=='F_DS2D' and self.nlogs==1:
                f = isam2_f_glc_t.decode (e.data)
                self.add_ds_factor (f, li)
                if li==0 and f.utime > self.utime: 
                    self.publish (est_log)
                    self.utime = f.utime
                self.solve ()
                sol = Centralized_solution (self.ids, self.nodes, self.x, self.cov)
                self.sols.append (sol)
            elif e.channel=='F_RANGE2D':
                f = isam2_f_pose_pose_partial_t.decode (e.data)
                if li==0 and f.utime > self.utime: 
                    self.publish (est_log)
                    self.utime = f.utime
                self.add_range_factor (f)
                self.rnodes.append ((f.node_id1, f.node_id2))
                #self.solve ()
                #sol = Centralized_solution (self.ids, self.nodes, self.x, self.cov)
                #self.sols.append (sol)
            li,e = self.next_event ()

        # save list of solutions
        with open ('solutions.pkl', 'wb') as f:
            pickle.dump (self.sols, f)
        with open ('rangenodes.pkl', 'wb') as f:
            pickle.dump (self.rnodes, f)

        # recover state at conclusion
        if len (self.nodes) < 6.8e3:
            print '{Centralized} recovering mean AND cov'
            self.solve (recover_cov=True)
        else:
            print '{Centralized} recovering mean NOT cov'
            self.solve (recover_cov=False)
        print '{Centralized} added %d nodes' % (len (self.nodes))

class Centralized_solution (object):
    def __init__ (self, ids, nodes, x, cov):
        self.ids = ids
        self.nodes = np.asarray (nodes)
        self.x = x
        self.cov = cov

if __name__ == '__main__':
    import cPickle as pickle

    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog0> [<lcmlog1> ... <lcmlogN>]' % sys.argv[0]
        sys.exit (0)

    logs = [lcm.EventLog (f) for f in sys.argv[1:]]
    post = Centralized (logs)
    post.run (logs)

    sol = Centralized_solution (post.ids, post.nodes, post.x, post.cov)
    if post.nlogs==1: pklname = 'decentral_sol.pkl'
    else: pklname = 'central_sol.pkl'
    with open (pklname, 'wb') as f:
        pickle.dump (sol, f)

    # plot everything
    color = ['r','b','k']
    fig = plt.figure (figsize=(8,10))

    ax_path = plt.subplot2grid ((3,2), (0,0), rowspan=2, colspan=2)
    ax_sig = plt.subplot2grid ((3,2), (2,0), rowspan=1, colspan=2)

    for ii,c in zip (post.ids.itervalues (), color):
        if post.nlogs==1:
            jj = np.where (np.asarray (post.nodes) > 1e5)[0]
            kk = np.where (np.asarray (post.nodes) < 1e5)[0]
            ax_path.plot (post.x[jj,1], post.x[jj,0], '.-', c=c)
            ax_path.plot (post.x[kk,1], post.x[kk,0], '.-', c='k')

            #print 'last tol node:', post.nodes[kk[-1]]
        else:
            jj = ii
            kk = np.where ((np.asarray (post.nodes) < 1e5) & (np.asarray (post.nodes) >= 1e4) )[0]
            ll = np.where ((np.asarray (post.nodes) < 1e4) & (np.asarray (post.nodes) >= 1e3) )[0]
            ax_path.plot (post.x[jj,1], post.x[jj,0], '.-', c=c)
            ax_path.plot (post.x[kk,1], post.x[kk,0], '.-', c='k')
            ax_path.plot (post.x[ll,1], post.x[ll,0], '.-', c='b')

        t = (np.asarray (post.node_utime)[jj] - post.node_utime[0])*1e-6
        sigx = np.sqrt (post.cov[jj,0])
        sigy = np.sqrt (post.cov[jj,3])
        ax_sig.plot (t, 3*sigx, '-', c=c)
        ax_sig.plot (t, 3*sigy, '--', c=c)

    ax_path.axis ('equal')
    ax_path.set_ylim ([-300,200])
    ax_path.grid ()
    ax_sig.set_ylim ([0,50])

    plt.show ()

    sys.exit (0)
