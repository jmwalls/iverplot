#!/usr/bin/env python
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc ("text", usetex=True)
rc ("font", family="serif")
rc ("font", size=18)
rc ("legend", fontsize=14)
rc ("axes", labelsize=18)

iver28d = 1e3*np.array ([0.00002300, 0.00008702, 0.00009137, 0.00010660, 0.00003485, 0.00009256, 0.00003956])
topd = 1e3*np.array ([0.00005261, 0.00007690 ,0.00009166 ,0.00009884 ,0.00004937 ,0.00008429 ,0.00006345])

if __name__ == '__main__':

    N = iver28d.size

    ind = np.arange (N)  # the x locations for the groups
    width = 0.17         # the width of the bars

    #fig = plt.figure (figsize=(10,5))
    #fig = plt.figure (figsize=(18,5))
    fig = plt.figure (figsize=(12,3.5))
    ax = fig.add_subplot (111)

    irects = ax.bar (ind+0.5-width, iver28d, width, color='r', hatch='//', alpha=0.9)
    trects = ax.bar (ind+0.5, topd, width, color='b', hatch='xx', alpha=0.9)

    # add some
    #ax.set_ylabel ('CEIF/DEIF difference [m]')
    ax.set_ylabel ('CEIF/DEIF difference [mm]')
    ax.set_xlabel ('Experiment label')
    ax.set_xticks (ind+0.5)
    ax.set_xticklabels (('A','B','C','D','E','F','G'))

    ax.legend ((irects[0], trects[0]), ('AUV2', 'Topside'))

    #ax.axhline (1e-4, color='k', lw=3)
    #ax.text (0.25,1.05e-4,'$10^{-4}$ m error',fontsize=18)
    ax.axhline (1e3*1e-4, color='k', lw=3)
    ax.text (0.10,1e3*1.05e-4,'$10^{-4}$ m error',fontsize=18)

    #def autolabel(rects):
    #    # attach some text labels
    #    for rect in rects:
    #        height = rect.get_height()
    #        ax.text (rect.get_x ()+rect.get_width()/2., height+0.0001, '%0.1e'%height, ha='center', va='bottom')

    #autolabel (irects_mean)
    #autolabel (irects_max)
    #autolabel (trects_mean)
    #autolabel (trects_max)

    fig.savefig ('ceifdeif.pdf', transparent=True, bbox_inches='tight', pad_inches=0)
    plt.show ()

    sys.exit (0)
