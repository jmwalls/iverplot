"""
utility for parsing lcmtypes from logfile into times series types
"""
import re
import numpy as np

import lcm

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
