#!/usr/bin/env python
"""
cook client lcmlog-graph-manager:
    remove server pose-graph, i.e., all server prior/glc/odometry factors
    keep range factors
"""
import sys

import lcm
from perls.lcmtypes.perllcm import isam2_f_prior_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_t

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog-graph-manager>' % sys.argv[0]
        sys.exit (0)

    ilog = lcm.EventLog (sys.argv[1])
    olog = lcm.EventLog ('lcmlog-graph-manager-cooked', 'w', overwrite=True)

    for e in ilog:
        if e.channel=='F_GLC2D':
            continue
        elif e.channel=='F_PRIOR2D':
            f = isam2_f_prior_t.decode (e.data)
            if f.node_id < 1e5: continue
        elif e.channel=='F_ODO2D':
            f = isam2_f_pose_pose_t.decode (e.data)
            if f.node_id1 < 1e5: continue
        olog.write_event (e.timestamp, e.channel, e.data)

    sys.exit (0)
