#!/usr/bin/env python
import sys
import os
import time


if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <divedir/>' % sys.argv[0]
        sys.exit (0)

    fname = os.path.join (sys.argv[1], 'timerange')
    with open (fname, 'r') as f:
        tr = f.readlines ()

    start = time.strptime (tr[1][12:].strip (), '%a %b %d %H:%M:%S %Y')
    end = time.strptime (tr[2][10:].strip (), '%a %b %d %H:%M:%S %Y')

    secs = time.mktime (end) - time.mktime (start)
    print 'mission time : %0.3f hours' % (secs/3600.)

    sys.exit (0)
