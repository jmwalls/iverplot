#!/usr/bin/env python
"""
cook client lcmlog:
    replace acoustically reported osp with full precision packets from server
    log.
"""
import sys

import numpy as np

import lcm
from perls.lcmtypes.senlcm import acomms_osp_t

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <lcmlog-orig> <lcmlog-server>' % sys.argv[0]
        sys.exit (0)

    logc = lcm.EventLog (sys.argv[1])

    logs = lcm.EventLog (sys.argv[2])
    osp_events = [e for e in logs if e.channel=='IVER31_SERVER_OSP']
    osp = [acomms_osp_t.decode (e.data) for e in osp_events]
    osp_utime = np.asarray ([o.utime for o in osp])
    print 'found %d osps' % len (osp_utime)

    olog = lcm.EventLog ('lcmlog-replaced-osp', 'w', overwrite=True)
    for e in logc:
        if e.channel=='IVER28_CLIENT_OSP':
            m = acomms_osp_t.decode (e.data)

            ii = np.where ((m.utime-osp_utime>0) & (m.utime-osp_utime < 5e6))[0]
            #ii = np.where ((m.utime-osp_utime>-12e6) & (m.utime-osp_utime < 12e6))[0]
            #print (m.utime-osp_utime[ii])*1e-6
            #print [osp[i].new_tol_no for i in ii]
            for i in ii:
                if m.new_tol_no==osp[i].new_tol_no:
                    print 'replacing osp event (%d,%d) (%d,%d)' % (m.org_tol_no, m.new_tol_no, osp[i].org_tol_no, osp[i].new_tol_no)
                    olog.write_event (e.timestamp, e.channel, osp[i].encode ())
        else:
            olog.write_event (e.timestamp, e.channel, e.data)

    sys.exit (0)
