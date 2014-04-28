import sys

import lcm
from perls.lcmtypes.perllcm import isam2_f_prior_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_partial_t

if __name__ == '__main__':
    log = lcm.EventLog (sys.argv[1])

    for e in log:
        if e.channel=='F_PRIOR2D':
            f = isam2_f_prior_t.decode (e.data)
            if f.node_id < 1e5:
                print f.utime, f.node_id
        elif e.channel=='F_ODO2D':
            f = isam2_f_pose_pose_t.decode (e.data)
            if f.node_id1 < 1e5:
                print f.utime, f.node_id1
            if f.node_id2 < 1e5:
                print f.utime, f.node_id2
        elif e.channel=='F_RANGE2D':
            f = isam2_f_pose_pose_partial_t.decode (e.data)
            if f.node_id1 < 1e5:
                print f.utime, f.node_id1
            if f.node_id2 < 1e5:
                print f.utime, f.node_id2

    sys.exit (0)
