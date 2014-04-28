#!/usr/bin/env python
"""
post-owtt nav check---perform first-order checks on quality of dive data


plot the following:
    * owtt ranges from each source
    * lbl ranges to each beacon
    * vehicle trajectory
        * iver state from uvc messages
        * valid gps
        * computed lbl position fixes
"""

import sys
import os

import numpy as np
import matplotlib.pyplot as plt

import lcm
from bot_param import update_t
from perls.lcmtypes.senlcm import acomms_range_t, gpsd3_t, gpsd3_fix_t
from perls.lcmtypes.perllcm import iver_state_t

from perls import BotParam


def param_from_log (lcmlog):
    param = None
    while (True):
        e = lcmlog.read_next_event ()
        if 'PARAM_UPDATE' in e.channel:
            p = update_t.decode (e.data)
            with open ('tmp_param.cfg', 'w') as f:
                lines, save_line = [], False
                for line in p.params.splitlines ():
                    if 'INCLUDE = [' in line: continue
                    else: lines.append (line)
                f.write ('\n'.join (lines))
            param_args = BotParam.bot_param_args_to_pyargv ('tmp_param.cfg', 'false', '')
            param = BotParam.BotParam (param_args)
            os.remove ('tmp_param.cfg')
            break
    log.seek (0)
    return param

def plot_state (chan, lcmlog):
    state = [iver_state_t.decode (e.data) for e in log if e.channel==state_chan]
    x = np.array ([s.position.xyzrph[0] for s in state])
    y = np.array ([s.position.xyzrph[1] for s in state])

    fig = plt.figure (figsize=(10,10))
    ax = fig.add_subplot (111)
    ax.plot (x, y, '.-')
    return state


def plot_lbl_ranges (nlbl, acomms_ranges):
    lbl_ranges, lbl_utimes = {}, {}
    for i in range (nlbl):
        lbl_ranges[i], lbl_utimes[i] = [], []
    for r in acomms_ranges:
        if r.type != acomms_range_t.NARROWBAND_LBL: continue
        for i in range (nlbl):
            if np.isnan (r.owtt[i]) or r.owtt[i]<=0: continue
            lbl_ranges[i].append (r.owtt[i])
            lbl_utimes[i].append (r.utime)
    fig = plt.figure (figsize=(10,5))
    ax = fig.add_subplot (111)
    marker = ['r.-', 'g.-', 'bx-']
    for i in range (nlbl):
        print 'lbl src %d : %d' % (i, len (lbl_ranges[i]))
        ax.plot (lbl_utimes[i], lbl_ranges[i], marker[i], label='lbl %d'%i)
    ax.legend ()

def plot_owtt_ranges (acomms_ranges):
    owtts = {}
    utimes = {}
    for r in acomms_ranges:
        if r.type != acomms_range_t.ONE_WAY_SYNCHRONOUS: continue
        if np.isnan (r.owtt[0]) or r.owtt[0]<=0: continue
        if not r.src in owtts:
            owtts[r.src] = [r.owtt[0]]
            utimes[r.src] = [r.utime]
        else:
            owtts[r.src].append (r.owtt[0])
            utimes[r.src].append (r.utime)
    fig = plt.figure (figsize=(10,5))
    ax = fig.add_subplot (111)
    marker = ['r.-', 'g.-', 'bx-']
    for i,k in enumerate (owtts.iterkeys ()):
        if k<0: continue
        print 'owtt src %d : %d' % (k, len (owtts[k]))
        ax.plot (utimes[k], owtts[k], marker[i])

if __name__ == '__main__':
    if len (sys.argv) < 2:
        print 'usage: %s <lcmlog>' % sys.argv[0]
        sys.exit (0)

    try:
        log = lcm.EventLog (sys.argv[1])
    except Exception as err:
        print 'error opening lcmlog: %s' % err

    param = param_from_log (log)
    if not param:
        print 'Could not find param file'
        sys.exit (0)

    # data channels
    vehicle = param.get_str ('vehicle.name')

    gpsd_chan = param.get_str ('sensors.gpsd3-client.gsd.channel')
    range_chan = param.get_str ('sensors.modem.range_channel')
    sync_chan = param.get_str ('sensors.modem.sync_channel')

    if vehicle != 'topside':
        state_chan = param.get_str ('vehicle.state_channel')
        state = plot_state (state_chan, log)

    acomms_ranges = [acomms_range_t.decode (e.data) for e in log if e.channel==range_chan]
    nlbl = param.get_num_subkeys ('lbl.network')
    plot_lbl_ranges (nlbl, acomms_ranges)
    plot_owtt_ranges (acomms_ranges)

    plt.show ()

    sys.exit (0)
