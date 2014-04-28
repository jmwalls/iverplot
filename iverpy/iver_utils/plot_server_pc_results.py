#!/usr/bin/env python
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=18)
rc ("legend", fontsize=16)
rc ("axes", labelsize=18)

iver28_mean = 1e3*np.array ([0.00000468, 0.00008109, 0.00007058, 0.00006569, 0.00003784, 0.00004584, 0.00003954]) 
iver28_max  = 1e3*np.array ([0.00000953, 0.00059813, 0.00041480, 0.00101610, 0.00015408, 0.00029855, 0.00029955]) 

top_mean = 1e3*np.array ([0.00000684, 0.00006363, 0.00005682, 0.00006332, 0.00003767, 0.00003963, 0.00003756])
top_max  = 1e3*np.array ([0.00001327, 0.00053984, 0.00039471, 0.00101610, 0.00015408, 0.00029855, 0.00016075])

if __name__ == '__main__':

    N = iver28_mean.size

    ind = np.arange (N)  # the x locations for the groups
    width = 0.17         # the width of the bars

    #fig = plt.figure (figsize=(16,5))
    fig = plt.figure (figsize=(12,3.5))
    ax = fig.add_subplot (111)

    irects_mean = ax.bar (ind, iver28_mean, width, color='r', alpha=0.9)
    irects_max = ax.bar (ind+width, iver28_max, width, color='r', hatch='//', alpha=0.5)

    trects_mean = ax.bar (ind+0.5, top_mean, width, color='b', alpha=0.9)
    trects_max = ax.bar (ind+0.5+width, top_max, width, color='b', hatch='xx', alpha=0.5)

    # add some
    #ax.set_ylabel ('Reconstruction error [m]')
    ax.set_ylabel ('Reconstruction error [mm]')
    ax.set_xlabel ('Experiment label')
    ax.set_xticks (ind+0.5)
    ax.set_xticklabels (('A','B','C','D','E','F','G'))

    ax.legend ((irects_mean[0], irects_max[0], trects_mean[0], trects_max[0]), 
            ('AUV2 Mean', 'AUV2 Max', 'Topside Mean', 'Topside Max'))

    #ax.axhline (1e-4, color='k', lw=3)
    #ax.text (0.25,1.2e-4,'$10^{-4}$ m error',fontsize=18)
    ax.axhline (1e3*1e-4, color='k', lw=3)
    ax.text (0.10,1e3*1.2e-4,'$10^{-4}$ m error',fontsize=18)

    #def autolabel(rects):
    #    # attach some text labels
    #    for rect in rects:
    #        height = rect.get_height()
    #        ax.text (rect.get_x ()+rect.get_width()/2., height+0.0001, '%0.1e'%height, ha='center', va='bottom')

    #autolabel (irects_mean)
    #autolabel (irects_max)
    #autolabel (trects_mean)
    #autolabel (trects_max)

    fig.savefig ('pgerrorbar.pdf', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.show ()

    sys.exit (0)
