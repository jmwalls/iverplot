#!/usr/bin/env python
"""
compute number of backup packets/recovery packets used
"""
import sys

import lcm
from perls.lcmtypes.senlcm import acomms_osp_t
from perls.lcmtypes.senlcm import acomms_osp_recovery_t
from perls.lcmtypes.senlcm import acomms_range_t

class Client (object):
    def __init__ (self, lcmpath):
        url = ''.join (['file://', 
                        lcmpath,
                        '?speed=0'])
        self.lc = lcm.LCM (url)
        self.lc.subscribe ('TOPSIDE_CLIENT_OSP', self.osp_handler)
        self.lc.subscribe ('TOPSIDE_CLIENT_RECOVERY', self.recovery_handler)
        self.lc.subscribe ('TOPSIDE_ACOMMS_RANGE', self.range_handler)

        self.osps = []
        self.org_no = 0
        self.tol_no = 0

        self.osp_dict = {i:0 for i in range (3)}
        self.recovery = 0

    def osp_handler (self, channel, data):
        osp = acomms_osp_t.decode (data)
        self.osps.append (osp)

    def recovery_handler (self, channel, data):
        rec = acomms_osp_recovery_t.decode (data)
        if self.tol_no > rec.new_tol_no: return
        if self.tol_no != rec.org_tol_no: return

        self.tol_no = rec.new_tol_no
        self.org_no = rec.org_tol_no

        self.recovery += 1

    def range_handler (self, channel, data):
        msg = acomms_range_t.decode (data)
        if msg.type != acomms_range_t.ONE_WAY_SYNCHRONOUS:
            return

        self.osps[:] = [o for o in self.osps if o.utime==msg.utime]
        if not self.osps: return

        ospid = len (self.osps)-1
        while self.osps:
            osp = self.osps.pop ()
            org_no, new_no = osp.org_tol_no, osp.new_tol_no

            if new_no <= self.tol_no or org_no < self.org_no:
                #print ospid, 'already have this info'
                pass
            elif org_no > self.tol_no and self.tol_no != 0:
                print 'uh oh!'
            elif org_no == self.org_no or org_no == self.tol_no or self.tol_no==0:
                print ospid, 'adding new osp'
                self.org_no = org_no
                self.tol_no = new_no
                self.osp_dict[ospid] += 1
            ospid -= 1 

        del self.osps[:]

    def run (self):
        try:
            while True:
                self.lc.handle ()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-client>' % sys.argv[0]
        sys.exit (0)

    client = Client (sys.argv[1])
    client.run ()
    print 'osps', client.osp_dict
    print 'recs', client.recovery

    sys.exit (0)
