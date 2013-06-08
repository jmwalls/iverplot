"""
Unit conversion module
"""

import numpy as np

def second_to_microsecond (s):
    return 1e6*s

def degree_to_radian (a):
    return a*np.pi/180.

def radian_to_degree (a):
    return a*180./np.pi

def knot_to_meter_per_second (s):
    return s*0.514444444
