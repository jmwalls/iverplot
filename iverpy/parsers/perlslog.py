"""
Time series class definition for perls lcmtypes
"""
from perls.lcmtypes.senlcm import acomms_osp_t
from perls.lcmtypes.senlcm import acomms_range_t
from perls.lcmtypes.senlcm import dstar_ssp1_t
from perls.lcmtypes.senlcm import gpsd3_t, gpsd3_fix_t
from perls.lcmtypes.senlcm import rdi_pd4_t
from perls.lcmtypes.senlcm import rph_t

from perls.lcmtypes.perllcm import isam2_node_t
from perls.lcmtypes.perllcm import iver_osm_vis_t, iver_osm_state_t
from perls.lcmtypes.perllcm import iver_state_t, position_t

from lcmlog import *

class Rph_series (Series):
    """
    rph 
    """
    def __init__ (self):
        super (Rph_series, self).__init__ (rph_t)
        self.rph = None

class Rdi_series (Series):
    """
    rdi
    """
    def __init__ (self):
        super (Rdi_series, self).__init__ (rdi_pd4_t)
        self.btv = None
        self.BTV_SENTINAL = None

        self.wtv = None
        self.WTV_SENTINAL = None

        self.range = None
        self.RANGE_SENTINAL = None

        self.altitude = None
        self.ALTITUDE_SENTINAL = None

        self.system_config = None
        self.btv_status = None
        self.wtv_status = None

class Dstar_series (Series):
    """
    dstar
    """
    def __init__ (self):
        super (Dstar_series, self).__init__ (dstar_ssp1_t)
        self.p_abs = None
        self.p_gage = None
        self.p_atm = None
        self.depth = None
        self.temperature = None

class Gpsd_fix_series (Series):
    """
    Gpsd fix
    """
    def __init__ (self):
        super (Gpsd_fix_series, self).__init__ (gpsd3_fix_t)
        self.latitude = None
        self.longitude = None

        self.mode = None
        self.MODE_NOT_SEEN = None
        self.MODE_NO_FIX = None
        self.MODE_2D = None
        self.MODE_3D = None

class Gpsd_series (Series):
    """
    Gpsd
    """
    def __init__ (self):
        super (Gpsd_series, self).__init__ (gpsd3_t)
        self.fix = Gpsd_fix_series

        self.status = None
        self.STATUS_NO_FIX = None
        self.STATUS_FIX = None
        self.STATUS_DGPS_FIX = None

        self.satellites_used = None

class Position_series (Series):
    """
    Position
    """
    def __init__ (self):
        super (Position_series, self).__init__ (position_t)
        self.xyzrph = None
        self.xyzrph_cov = None

class Iver_state_series (Series):
    """
    Iver_state
    """
    def __init__ (self):
        super (Iver_state_series, self).__init__ (iver_state_t)
        self.position = Position_series

class Acomms_range_series (Series):
    """
    """
    def __init__ (self):
        super (Acomms_range_series, self).__init__ (acomms_range_t)
        self.src = None
        self.type = None
        self.owtt = None

        self.ONE_WAY_SYNCHRONOUS = None
        self.TWO_WAY_PING = None
        self.REMUS_LBL = None
        self.NARROWBAND_LBL = None

    def _user_format (self, msgs):
        owtt = self.owtt
        self.owtt = np.zeros ((owtt.shape[0], 4))
        for ii, o in enumerate (owtt):
            nowtt = min (len (o), 4)
            self.owtt[ii,:nowtt] = o[:nowtt]

class Osm_state_series (Series):
    """
    Osm_state
    """
    def __init__ (self):
        super (Osm_state_series, self).__init__ (iver_osm_state_t)
        self.index = None
        self.xy = None
        self.cov = None

class Osm_vis_series (Series):
    """
    Osm_vis
    """
    def __init__ (self):
        super (Osm_vis_series, self).__init__ (iver_osm_vis_t)
        self.nposes = None
        self.poses = Osm_state_series;

class Osp_series (Series):
    """
    Osp
    """
    def __init__ (self):
        super (Osp_series, self).__init__ (acomms_osp_t)
        self.new_tol_no = None
        self.org_tol_no = None

        self.Lambda = None
        self.eta = None

class Isam_node_series (Series):
    """
    Isam_node
    """
    def __init__ (self):
        super (Isam_node_series, self).__init__ (isam2_node_t)
        self.id = None
        self.mu = None
        self.cov = None

        self.node_type = None
        self.TYPE_POINT2D = None
        self.TYPE_POINT3D = None
        self.TYPE_POSE2D  = None
        self.TYPE_POSE3D  = None
        self.TYPE_PLANE3D = None
        self.TYPE_PLANE2D = None
        self.TYPE_ANCHOR2D = None
        self.TYPE_ANCHOR3D = None

class Iver (object):
    def __init__ (self, logfile):
        log = lcm.EventLog (logfile)
        print '{Iver} parsing acomms range events...'
        self.acomms = parse_from_lcm (log, 'ACOMMS_RANGE', Acomms_range_series)

        print '{Iver} parsing dstar events...'
        self.dstar = parse_from_lcm (log, 'DESERT_STAR', Dstar_series)

        print '{Iver} parsing gpsd events...'
        #self.gpsd = parse_from_lcm (log, 'GPSD3', Gpsd_series)
        self.gpsd = parse_from_lcm (log, 'TOPSIDE_GPSD3', Gpsd_series)

        print '{Iver} parsing osm vis events...'
        self.osm = parse_from_lcm (log, 'OSM_VIS', Osm_vis_series)

        print '{Iver} parsing rdi events...'
        self.rdi = parse_from_lcm (log, 'RDI', Rdi_series)

        print '{Iver} parsing iver_state events...'
        self.state = parse_from_lcm (log, 'STATE', Iver_state_series)

        print '{Iver} parsing microstrain events...'
        self.ustrain = parse_from_lcm (log, 'MICROSTRAIN_ATTITUDE_BIAS', Rph_series)


if __name__ == '__main__':
    import sys
    import cPickle as pickle
    import matplotlib.pyplot as plt

    if len (sys.argv) < 2:
        print 'usage: %s <lcmfile>' % sys.argv[0]
        sys.exit (0)

    iver = Iver (sys.argv[1])

    print 'Pickling parsed Iver data...'
    with open ('iver.pkl', 'wb') as f:
        pickle.dump (iver, f)

    if not iver.state is None:
        plt.figure ()
        plt.plot (iver.state.position.xyzrph[:,1], iver.state.position.xyzrph[:,0], '.')
        plt.axis ('equal')
        plt.grid ()

        plt.show ()

    sys.exit (0)
