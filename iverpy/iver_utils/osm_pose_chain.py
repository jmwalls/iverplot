import numpy as np
import matplotlib.pyplot as plt

from plot_utils import draw_covariance

class Pose_chain (object):
    """
    pose-chain object for simple xy state

    Parameters
    -----------
    utime : utime of pose-graph
    ids : ids of poses
    xy :  list of xy poses
    cov : list of pose marginal covariances
    """
    def __init__ (self):
        self.utime = None
        self.nposes = 0
        self.ids = []
        self.xy = []
        self.cov = []

    def plot (self, ax, *args, **kwargs):
        ax.plot (self.xy[:,1], self.xy[:,0], *args, **kwargs)
        for xy,cov in zip (self.xy, self.cov):
            sig = cov.reshape ((2,2))
            draw_covariance (ax, xy, sig, 9., *args, **kwargs)

class Osm_series (object):
    """
    container for a time-series of pose-chains

    Parameters
    -----------
    pc : list of Pose_chain objects
    """
    def __init__ (self):
        self.pc = []

def iver_to_osm_series (osm):
    """
    pack an Osm_series object from an iver series object
    """
    osms = Osm_series ()
    nchains = len (osm.poses.index)
    for ii in range (nchains):
        pc = Pose_chain ()
        pc.utime = osm.utime[ii]
        pc.nposes = osm.nposes[ii]
        pc.ids = osm.poses.index[ii]
        pc.xy = osm.poses.xy[ii]
        pc.cov = osm.poses.cov[ii]
        osms.pc.append (pc)
    return osms

def isam_to_osm_series (isam_nodes):
    """
    pack an Osm_series object from an isam_nodes series object
    """
    osms = Osm_series ()
    pc = Pose_chain ()
    pc.utime = isam_nodes.utime
    pc.nposes = len (isam_nodes.utime)
    pc.ids = isam_nodes.id
    pc.xy = isam_nodes.mu
    pc.cov = isam_nodes.cov
    osms.pc.append (pc)
    return osms


if __name__ == '__main__':
    import sys
    import cPickle as pickle

    from lcmlog_perls import *

    if len (sys.argv) < 2:
        print 'usage: %s <iver.pkl>' % sys.argv[0]
        sys.exit (0)

    try:
        with open (sys.argv[1], 'rb') as f:
            iver = pickle.load (f)
    except Exception as err:
        print 'error loading pickle: %s' % err
        sys.exit (0)

    # let's just look at the last for now...
    osm_series = iver_to_osm_series (iver.osm)
    pc = osm_series.pc[-1]

    # plot the pose graphs
    fig = plt.figure (figsize=(10,10))
    ax = fig.add_subplot (111)
    pc.plot (ax, 'b', lw=2)
    ax.axis ('equal')
    ax.grid ()
    plt.show ()

    sys.exit (0)
