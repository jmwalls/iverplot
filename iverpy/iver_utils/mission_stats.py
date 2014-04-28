#!/usr/bin/env python
import sys
import cPickle as pickle

import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt

import lcm
from perls.lcmtypes.senlcm import acomms_osp_t
from perls.lcmtypes.senlcm import acomms_osp_recovery_t

class Acoustic_node (object):
    def __init__ (self, log, osp_chan, rec_chan):
        print '{Acoustic_node} parsing OSP events...'
        #self.osps = [acomms_osp_t.decode (e.data) for e in log if osp_chan in e.channel]
        osps = [acomms_osp_t.decode (e.data) for e in log if osp_chan in e.channel]
        print '{Acoustic_node} found %d OSPs' % (len (osps))

        print '{Acoustic_node} parsing OSP recovery events...'
        #self.recs = [acomms_osp_recovery_t.decode (e.data) for e in log if rec_chan in e.channel]
        recs = [acomms_osp_recovery_t.decode (e.data) for e in log if rec_chan in e.channel]
        print '{Acoustic_node} found %d recoveries' % (len (recs))

        t_osp = [o.utime for o in osps]
        t_rec = [o.utime for o in recs]

        self.t_osp = np.asarray (t_osp)
        self.t_rec = np.asarray (t_rec)
        utime = t_osp+t_rec
        utime.sort ()
        self.utime = np.asarray (utime)

def used_recovery (node):
    """
    how often does the client use the recovery
    """
    pass

def reception_rate (tx_utime, rx_utime):
    """
    Compute reception rate 
    
    Parameters
    -----------
    tx_utime : times-of-launch
    rx_utime : times-of-arrival
    """
    t0 = rx_utime[0] - 5e-6 # to account for lag 
    tf = rx_utime[-1] 
    index = np.argwhere ((tx_utime>t0) &(tx_utime<tf))
    print 'reception rate = %f %%' %  (float (len (rx_utime)) /len (index) * 100)

def average_throughput (utimes, win_size, step):
    """ 
    Find average throughput over sliding window (approximately) 

    Returns time, throughput tuple
                        
    Parameters
    -----------
    utime : array of message utimes
    win_size : length of sliding window (in seconds)
    """
    t_bits = np.floor (utimes*1.e-6)
    t0 = t_bits[0] 
    tf = t_bits[-1]
    t = np.around (np.arange (t0, tf, step), 1)

    index = np.in1d (t, t_bits) # indices of t that received

    bits = np.zeros (len (t), dtype='float64') 
    bits[index] = 192.*8.*(1./step) # bits received at t_data 

    sz = int (win_size/step) 
    win = (1./sz)*np.ones (sz) 
    throughput = np.convolve (bits, win, mode='same') 
    
    return t, throughput


if __name__ == '__main__':
    if len (sys.argv) < 3:
        print 'usage: %s <lcmlog-server> <lcmlog-client>' % sys.argv[0]
        sys.exit (0)

    if 'pkl' in sys.argv[1]:
        with open (sys.argv[1], 'rb') as f:
            server = pickle.load (f)
    else:
        logs = lcm.EventLog (sys.argv[1])
        server = Acoustic_node (logs, 'SERVER_OSP', 'SERVER_RECOVERY')
        with open ('stats_server.pkl', 'wb') as f:
            pickle.dump (server, f)

    if 'pkl' in sys.argv[2]:
        with open (sys.argv[2], 'rb') as f:
            client = pickle.load (f)
    else:
        logc = lcm.EventLog (sys.argv[2])
        client = Acoustic_node (logc, 'CLIENT_OSP', 'CLIENT_RECOVERY')
        with open ('stats_client.pkl', 'wb') as f:
            pickle.dump (client, f)

    reception_rate (server.utime, client.utime)

    #win = 10*60 # 10 minute window
    win = 3*60 # 5 minute window
    tc, bc = average_throughput (client.utime, win, 1)
    splinec = interpolate.UnivariateSpline (tc, bc)
    tsc = np.arange (tc[0], tc[-1])
    bsc = splinec (tsc)

    ts, bs = average_throughput (server.utime, win, 1)
    splines = interpolate.UnivariateSpline (ts, bs)
    tss = np.arange (ts[0], ts[-1])
    bss = splines (tss)

    fig = plt.figure (figsize=(12,6))
    ax = fig.add_subplot (111)

    t0 = min (tsc[0], tss[0])
    ax.plot ((tss-t0)/3600., bss, 'g', lw=2, label='100% reception')
    ax.plot ((tsc-t0)/3600., bsc, 'b', lw=2, label='Actual')
    ax.plot ((ts-t0)/3600., bs, 'g', lw=1)
    ax.plot ((tc-t0)/3600., bc, 'b', lw=1)

    ax.legend (loc=4)
    ax.set_ylabel ('throughput [bps]')
    ax.set_xlabel ('time [hours]')
    ax.set_title ('Average bandwidth over %d minute sliding window' % int (win/60))

    plt.show ()

    sys.exit (0)
