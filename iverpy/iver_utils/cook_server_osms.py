#!/usr/bin/env python
"""
cook server lcmlog-server:
    shift tol_no. used for when the estimator was started before the logger.
"""
import sys

import lcm
from perls.lcmtypes.perllcm import iver_osm_state_t
from perls.lcmtypes.perllcm import iver_osm_vis_t
from perls.lcmtypes.senlcm import acomms_osp_t

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-server>' % sys.argv[0]
        sys.exit (0)

    ilog = lcm.EventLog (sys.argv[1])
    olog = lcm.EventLog ('lcmlog-server-cooked', 'w', overwrite=True)
    
    DTOL = 2
    for e in ilog:
        if e.channel=='IVER31_SERVER_OSP':
            m = acomms_osp_t.decode (e.data)
            m.org_tol_no += DTOL
            m.new_tol_no += DTOL
            olog.write_event (e.timestamp, e.channel, m.encode ())
            continue
        elif e.channel=='SERVER_OSM_VIS':
            m = iver_osm_vis_t.decode (e.data)
            for p in m.poses: p.index += DTOL
            olog.write_event (e.timestamp, e.channel, m.encode ())
            continue
        olog.write_event (e.timestamp, e.channel, e.data)

    sys.exit (0)
