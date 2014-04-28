import sys

import numpy as np
import matplotlib.pyplot as plt

import lcm
from perls.lcmtypes.senlcm import acomms_data_type_t
from perls.lcmtypes.senlcm import acomms_tdma_sync_t
from perls.lcmtypes.senlcm import acomms_range_t

if __name__ == '__main__':
    logs = lcm.EventLog (sys.argv[1])
    logc = lcm.EventLog (sys.argv[2])

    sync = [acomms_tdma_sync_t.decode (e.data) for e in logs if e.channel=='IVER31_ACOMMS_SYNC']
    owtts = [acomms_range_t.decode (e.data) for e in logs if e.channel=='IVER31_ACOMMS_RANGE']
    owttc = [acomms_range_t.decode (e.data) for e in logc if e.channel=='IVER28_ACOMMS_RANGE']

    tos = np.asarray ([o.utime for o in owtts if o.type==acomms_range_t.ONE_WAY_SYNCHRONOUS])
    cms = np.asarray ([o.receiver_clk_mode for o in owtts if o.type==acomms_range_t.ONE_WAY_SYNCHRONOUS])

    toc = np.asarray ([o.utime for o in owttc if o.type==acomms_range_t.ONE_WAY_SYNCHRONOUS])
    cmc = np.asarray ([o.receiver_clk_mode for o in owttc if o.type==acomms_range_t.ONE_WAY_SYNCHRONOUS])

    ts = np.asarray ([s.utime for s in sync if s.dt.type==acomms_data_type_t.DATA])
    to = np.asarray ([o.utime for o in owttc if o.src==3])

    plt.figure ()
    plt.plot ((ts-ts[0])*1e-6, np.ones (len (ts)), 'bo')
    plt.plot ((to-ts[0])*1e-6, np.ones (len (to)), 'r.')

    plt.figure ()
    plt.plot ((tos-ts[0])*1e-6, cms, 'r',lw=3)
    plt.plot ((toc-ts[0])*1e-6, cmc, 'b',lw=1.5)

    plt.show ()
    sys.exit (0)
