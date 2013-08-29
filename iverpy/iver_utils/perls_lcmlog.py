"""
utility for parsing perls lcmtypes from logfile into times series types
"""

import re
import numpy as np

import lcm
from perls.lcmtypes.senlcm import acomms_range_t
from perls.lcmtypes.senlcm import dstar_ssp1_t
from perls.lcmtypes.senlcm import gpsd3_t, gpsd3_fix_t
from perls.lcmtypes.senlcm import rdi_pd4_t
from perls.lcmtypes.senlcm import rph_t

from perls.lcmtypes.perllcm import iver_osm_vis_t, iver_osm_state_t
from perls.lcmtypes.perllcm import iver_state_t, position_t

def parse_from_lcm (lcmlog, channel, Series_type, msgs=None, sub_prefix=None):
    """
    shoddy way to fill a time-series lcm object from an lcmlog.

    series_obj should have the same field names as the lcm object (for fields
    that the user wants to parse).

    note that we will assume all tuple fields are of constant length, i.e.,
    variable length arrays will crash this!

    Parameters
    -----------
    lcmlog : lcm EventLog object
    channel : channel name of data
    lcmtpe : type of lcm object on channel
    Series_type : series type
    msgs : parsed messages from lcmlog (so we can call recursively)
    """
    series_obj = Series_type ()
    lcmtype = series_obj.lcmtype

    ser_attrs = [d for d in dir (series_obj) if not d.startswith ('_') and not getattr (series_obj, d)]

    sub_attrs = [d for d in dir (series_obj) if not d.startswith ('_') and getattr (series_obj, d)]
    sub_attrs.remove ('lcmtype')

    for sa in ser_attrs:
        if not hasattr (lcmtype, sa):
            raise Exception ('%s attribute not in lcmtype!' % sa)

    # first find enum types/consts/static fields
    const_attrs = [sa for sa in ser_attrs if sa.isupper ()]
    for ca in const_attrs:
        setattr (series_obj, ca, getattr (lcmtype, ca))

    # parse log for messages
    if not msgs:
        pattern = re.compile ('^.*%s$' % channel)
        msgs = [lcmtype.decode (e.data) for e in lcmlog if re.match (pattern, e.channel)]
        if not len (msgs):
            print '{lcmlog-export} no messages found in log!'
            return None

    # fill list of vals for each attr
    var_attrs = [sa for sa in ser_attrs if not sa.isupper ()]
    vals = {va : [] for va in var_attrs}
    for m in msgs:
        for va in var_attrs:
            if sub_prefix: obj = getattr (m, sub_prefix) # should really split sub_prefix on '.'
            else: obj = m

            if type (obj) is list:
                val = np.asarray ([getattr (o, va) for o in obj])
            else:
                val = getattr (obj, va)

            vals[va].append (val)

    # set series object series attributes
    for k,v in vals.iteritems ():
        val_type = type (v[0])
        print '{lcmlog-export} adding %s of type %s' % (k, val_type)
        if val_type is tuple:
            setattr (series_obj, k, np.asarray (v))
        elif val_type is int or val_type is float:
            setattr (series_obj, k, np.asarray (v))
        else:
            setattr (series_obj, k, v)

    # handle nested types recursively
    for sa in sub_attrs:
        ser_type = getattr (series_obj, sa)
        print '{lcmlog-export} finding nested types', sa
        if sub_prefix: sp = '.'.join ([sub_prefix, sa])
        else: sp = sa
        val = parse_from_lcm (lcmlog, channel, ser_type, msgs, sp)
        #print 'setting %s as type %s' % (sa, type (val))
        setattr (series_obj, sa, val)

    # call custom formatting
    series_obj._user_format (msgs)

    return series_obj


class Series (object):
    """
    series base class

    Parameters
    -----------
    utime : timestamps
    lcmtype : base lcmtype of series

    Methods
    --------
    _user_format : by default this method is empty, but users can overload to
        add custom formatting operations
    """
    def __init__ (self, lcmtype):
        self.utime = None
        self.lcmtype = lcmtype

    def _user_format (self, msgs):
        pass

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

class Iver (object):
    def __init__ (self, logfile):
        log = lcm.EventLog (logfile)
        print '{Iver} parsing acomms range events...'
        self.acomms = parse_from_lcm (log, 'ACOMMS_RANGE', Acomms_range_series)

        print '{Iver} parsing dstar events...'
        self.dstar = parse_from_lcm (log, 'DESERT_STAR', Dstar_series)

        print '{Iver} parsing gpsd events...'
        self.gpsd = parse_from_lcm (log, 'GPSD3', Gpsd_series)

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

    plt.figure ()
    plt.plot (iver.state.position.xyzrph[:,1], iver.state.position.xyzrph[:,0], '.')
    plt.axis ('equal')
    plt.grid ()

    plt.show ()

    sys.exit (0)
