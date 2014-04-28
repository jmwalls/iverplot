#!/usr/bin/env python
"""
cook server lcmlog-graph-manager:
    shift tol_no. used for when the estimator was started before the logger.
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

    DTOL = 2
    for e in ilog:
        if e.channel=='F_PRIOR2D':
            f = isam2_f_prior_t.decode (e.data)
            if f.node_id < 1e5: 
                f.node_id += DTOL
                olog.write_event (e.timestamp, e.channel, f.encode ())
                continue
        elif e.channel=='F_ODO2D':
            f = isam2_f_pose_pose_t.decode (e.data)
            if f.node_id1 < 1e5: 
                f.node_id1 += DTOL
            if f.node_id2 < 1e5: 
                f.node_id2 += DTOL
            olog.write_event (e.timestamp, e.channel, f.encode ())
            continue
        olog.write_event (e.timestamp, e.channel, e.data)

    sys.exit (0)
