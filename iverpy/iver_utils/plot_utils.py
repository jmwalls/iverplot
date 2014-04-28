import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def draw_covariance (ax, mu, Sigma, k2, *args, **kwargs):
    e,V = np.linalg.eig((1./2)*(Sigma+Sigma.T));
    A = np.dot (V, np.diag (k2*e).astype (complex)**(1./2))
    A = np.real (A);
    t = np.arange (0,2*np.pi+0.1,0.1)
    c = np.vstack ((np.cos (t), np.sin (t)))
    y = np.dot (A, c) 
    y[0,:] += mu[0]
    y[1,:] += mu[1]
    ax.plot (y[1,:], y[0,:], *args, **kwargs)

class Picker_plot (object):
    """
    plot data so that a user can select points
    
    Parameters
    -----------
    ax : matplotlib ax instance
    data : Nx2 data array
    """
    def __init__ (self, ax, data, inliers=None):
        self.ax = ax
        self.data = data
        self.ax.figure.canvas.mpl_connect ('pick_event', self.on_pick)
        self.ax.figure.canvas.mpl_connect ('button_press_event', self.on_click)
        self.ax.figure.canvas.mpl_connect ('motion_notify_event', self.on_motion_notify)
        self.ax.figure.canvas.mpl_connect ('button_release_event', self.on_release)

        data_range = range (data.shape[0])
        if not inliers is None:
            self.inliers = list (inliers)
            self.outliers = list (np.setdiff1d (data_range, inliers))
        else:
            self.inliers = data_range
            self.outliers = []
        self.line = None
        self.oline = None

        self.rect = None
        self.x0 = None
        self.y0 = None
        
        self.draw ()

    def draw (self):
        if not self.line:
            self.line, = self.ax.plot (self.data[:,0], self.data[:,1], 'bo', picker=3)

        if self.oline:
            self.oline.remove ()
            self.oline = None

        self.oline, = self.ax.plot (self.data[self.outliers,0], 
                self.data[self.outliers,1], 'ro')

    def update_data (self, index):
        for ind in index:
            if ind in self.outliers: 
                print '{Picker_plot} user removed index:', ind
                self.inliers.append (ind)
                self.outliers.remove (ind)
            else:
                print '{Picker_plot} user added index:', ind
                self.outliers.append (ind)
                self.inliers.remove (ind)

        self.draw ()
        self.ax.figure.canvas.draw ()

    def on_pick (self, event):
        if event.artist != self.line: return
        self.update_data (event.ind)

    def on_click (self, event):
        toolbar = plt.get_current_fig_manager ().toolbar
        if toolbar.mode != '': return
        self.x0, self.y0 = event.xdata, event.ydata

    def on_motion_notify (self, event):
        if not self.x0 or not event.inaxes: return

        self.x1, self.y1 = event.xdata, event.ydata
        if self.rect:
            self.rect.remove ()
            self.rect = None
        self.rect = Rectangle ([self.x0,self.y0], event.xdata-self.x0,
                event.ydata-self.y0, color='k', fc='none',lw=1)
        self.ax.add_artist (self.rect)
        self.ax.figure.canvas.draw ()

    def on_release (self, event):
        if not self.x0: return
        if event.inaxes:
            self.x1, self.y1 = event.xdata, event.ydata
        x0 = min (self.x0, self.x1)
        y0 = min (self.y0, self.y1)
        x1 = max (self.x0, self.x1)
        y1 = max (self.y0, self.y1)

        self.x0,self.y0 = None, None
        self.x1,self.y1 = None, None
        if self.rect:
            self.rect.remove ()
            self.rect = None

        ind = np.where ((self.data[:,0]>x0) & (self.data[:,0]<x1) & (self.data[:,1]>y0) & (self.data[:,1]<y1))[0]
        self.update_data (ind)


if __name__ == '__main__':
    import sys

    data = np.random.rand (100,2)

    fig = plt.figure ()
    ax = fig.add_subplot (111)

    x = np.arange (0,1,0.01)
    y = 0.5*(np.cos (5*x)+1)
    ax.plot (x,y,'g')

    picker = Picker_plot (ax, data)
    plt.show ()

    sys.exit (0)
