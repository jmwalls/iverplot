#!/usr/bin/env python
"""
convert xy coordinate to lat/lon
"""

import sys

from perls import BotCore
from perls import BotParam


if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <x> <y>' % sys.argv[0]
        sys.exit (0)

    x = float (sys.argv[1])
    y = float (sys.argv[2])

    param_args = BotParam.bot_param_args_to_pyargv ('/home/jeff/perls/config/topside.cfg', 'false', '')
    param = BotParam.BotParam (param_args)

    orglatlon = param.get_double_array ('site.orglatlon')
    llxy = BotCore.BotGPSLinearize (orglatlon[0],orglatlon[1])

    lat,lon = llxy.to_ll (y,x)
    print 'converted xy = %0.3f,%0.3f to ll = %0.8f,%0.8f' % (x,y,lat,lon)

    sys.exit (0)
