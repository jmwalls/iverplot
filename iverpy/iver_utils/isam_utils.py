from time import time

import numpy as np

from perls.lcmtypes.perllcm import isam2_f_prior_t
from perls.lcmtypes.perllcm import isam2_f_pose_pose_partial_t

def timestamp_now ():
    return 1e6*time ()

def write_isam_prior2d (log, id0, x, R=(5.**2)*np.eye(2)):
    factor = isam2_f_prior_t ()
    factor.utime = timestamp_now ()
    factor.sub_type = isam2_f_prior_t.SUB_TYPE_FULL_STATE_POINT2D
    factor.node_id = id0
    factor.n = 2
    factor.z = list (x)
    factor.n2 = 4
    factor.R = R.ravel ().tolist ()
    log.write_event (factor.utime, 'F_PRIOR2D', factor.encode ())

def write_isam_prior3d (log, id0, x, R=(5.**2)*np.eye(3)):
    factor = isam2_f_prior_t ()
    factor.utime = timestamp_now ()
    factor.sub_type = isam2_f_prior_t.SUB_TYPE_FULL_STATE_POINT3D
    factor.node_id = id0
    factor.n = 3
    factor.z = list (x)
    factor.n2 = 9
    factor.R = R.ravel ().tolist ()
    log.write_event (factor.utime, 'F_PRIOR3D', factor.encode ())

def write_isam_range2d (log, id0, id1, z, R=0.5**2):
    factor = isam2_f_pose_pose_partial_t ()
    factor.utime = timestamp_now ()
    factor.sub_type = isam2_f_pose_pose_partial_t.SUB_TYPE_RANGE_POINT2D
    factor.node_id1 = id0
    factor.node_id2 = id1
    factor.n = 1
    factor.z = [z]
    factor.n2 = 1
    factor.R = [R]
    factor.m = 0
    log.write_event (factor.utime, 'F_RANGE2D', factor.encode ())

def write_isam_range3d (log, id0, id1, z, R=0.5**2):
    factor = isam2_f_pose_pose_partial_t ()
    factor.utime = timestamp_now ()
    factor.sub_type = isam2_f_pose_pose_partial_t.SUB_TYPE_RANGE_POINT3D
    factor.node_id1 = id0
    factor.node_id2 = id1
    factor.n = 1
    factor.z = [z]
    factor.n2 = 1
    factor.R = [R]
    factor.m = 0
    log.write_event (factor.utime, 'F_RANGE3D', factor.encode ())
