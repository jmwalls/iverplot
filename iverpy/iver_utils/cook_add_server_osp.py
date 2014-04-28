#!/usr/bin/env python
"""
cook client lcmlog:
    add server osp packets for post-process adding osp that were not
    transmitted real-time.
"""
import sys

import numpy as np

import lcm
from perls.lcmtypes.senlcm import acomms_data_t 
from perls.lcmtypes.senlcm import acomms_osp_t 
from perls.lcmtypes.senlcm import acomms_range_t 

if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <lcmlog-orig> <lcmlog-server>' % sys.argv[0]
        sys.exit (0)

    logc = lcm.EventLog (sys.argv[1])

    logs = lcm.EventLog (sys.argv[2])
    osp_events = [e for e in logs if e.channel=='IVER28_SERVER_OSP']
    osp = [acomms_osp_t.decode (e.data) for e in osp_events]
    osp_utime = np.asarray ([o.utime for o in osp])

    print 'found %d osps' % len (osp_utime)

    olog = lcm.EventLog ('lcmlog-multiple-server', 'w', overwrite=True)
    for e in logc:
        if e.channel=='TOPSIDE_ACOMMS_DATA':
            m = acomms_data_t.decode (e.data)
            print 'data', m.utime, m.src, m.frame_size

            if m.src==2 and m.frame_size==3:
                ii = np.where ((m.utime-osp_utime>0) & (m.utime-osp_utime < 5e6))[0]
                #print (m.utime-osp_utime[ii])*1e-6
                #print [osp[i].new_tol_no for i in ii]
                for i in ii:
                    olog.write_event (e.timestamp, 'TOPSIDE_CLIENT_OSP2', osp[i].encode ())
        else:
            olog.write_event (e.timestamp, e.channel, e.data)
        #elif e.channel=='TOPSIDE_CLIENT_OSP':
        #    m = acomms_osp_t.decode (e.data)
        #    print 'osp ', m.utime, m.new_tol_no
        #elif e.channel=='TOPSIDE_ACOMMS_RANGE':
        #    m = acomms_range_t.decode (e.data)
        #    print 'owtt', m.utime, m.src

    sys.exit (0)
