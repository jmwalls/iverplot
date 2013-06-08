"""
Iverplot---plot timeseries (and xy) data from Iver2 UVC and PeRL LCM logs

April 14, 2013
Jeff Walls <jmwalls@umich.edu>
"""

import os, sys

import pygtk
pygtk.require ('2.0')
import gtk

from matplotlib.figure import Figure
from matplotlib.widgets import MultiCursor
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg

from iverpy.parsers import UVCLog
from iverpy.plots import *

class NavigationToolbar (NavigationToolbar2GTKAgg):
    toolitems = [t for t in NavigationToolbar2GTKAgg.toolitems if t[0] in ('Home', 'Zoom')]

class Plot_item (object):
    """
    Plot_item represents a single subplot axis object

    Parameters
    -----------
    combobox : gtk.ComboBox drop-down selector box from main window, selects
        which plot object to display
    vbox : the gtk.VBox that contains the combobox, allows this object to
        redraw

    plot_object : instance of plot_object interface class

    Notes
    ------

    TODO
    -----
    write plot_object interface
        - plot_object base class should pack the combobox text

    Plot_item should hold a reference to the raw data

    should intelligently fill the combobox text maybe depending on the names
    of plot objects

    could be moved to another module, with the plot object base class
    """
    def __init__ (self, vbox, select_cb, uvclog=None, lcmlog=None):
        # gui material
        self.combobox = gtk.combo_box_new_text ()
        self.combobox.append_text ('Select plot:')

        # TODO some for loop that fills the combobox
        self.combobox.append_text ('temperature')
        self.combobox.append_text ('depth')
        self.combobox.append_text ('altitude')
        self.combobox.set_active (0)

        self.combobox.connect ('changed', self.on_combo_changed)
        self.combobox.connect ('changed', select_cb, self)

        self.vbox = vbox
        self.vbox.pack_start (self.combobox, fill=False, expand=False)

        self.combobox.show ()
        self.combobox.queue_draw ()

        # plot object
        self.plot_type = Plot_object (uvclog, lcmlog)

    def remove (self):
        self.vbox.remove (self.combobox)
        self.vbox.queue_draw ()

    def on_combo_changed (self, combo):
        model = combo.get_model ()
        index = combo.get_active ()
        
        if index > 0:
            #self.plot_type = model[index][0]
            # TODO select from plots
            pass

class Setwin (object):
    """
    Setwin implements the setwin functionality---allows the user to specify a
    time range to view timeseries data over the collection of subplots. this
    object should only exist as long as necessary for the user to select two
    end points, at which point the main window should destroy this object.

    Parameters
    -----------
    canvas : matplotlib gtk.DrawingArea backend, allows this object to call
        draw, and collect mouse events
    fig : the matplotlib figure, allows this object to access each axes object

    win_points : list of clicked points (up to two)
    vlines : vertical line objects to draw first selected boundary
    clicks : number of clicks---really just len (win_points)

    cursor : matplotlib.widgets.MultiCursor, draws vertical line over all
        current figure axes

    Notes
    ------

    TODO
    -----
    drawing vertical lines could be much more efficient:
        - is it possible to draw a single line across the entire drawing area,
          instead of a separate line for each axis?
        - use animation blit technique to update plot (no need to redraw every
          plot object, just the new vertical lines)... but is this really
          necessary?
        - add draw_cursor, that just looks cool, and more line matlab ginput 
        - see blit cursuring example:
            <http://www.scipy.org/Cookbook/Matplotlib/Animations>
            <http://matplotlib.org/users/event_handling.html>
        - matplotlib.widgets.MultiCursor looks perfect! SpanSelector is also
          really cool.
            <http://matplotlib.org/api/widgets_api.html>
            not sure if MultiCursor uses blit though...
    could be moved to another module
    """
    def __init__ (self, canvas, fig, complete_cb):
        self.canvas = canvas
        self.fig = fig
        self.complete = complete_cb

        self.canvas.mpl_connect ('button_press_event', self.on_canvas_clicked)

        self.win_points = []
        self.vlines = []
        self.clicks = 0

        self.cursor = MultiCursor (self.canvas, self.fig.axes, c='k', lw=1)
        self.canvas.draw ()

    def on_canvas_clicked (self, event):
        if event.inaxes is None: return

        if self.clicks == 0:
            self.win_points.append (event.xdata)
            for ax in self.fig.axes:
                self.vlines.append (ax.axvline (event.xdata,c='k',lw=1))
            self.canvas.draw ()
        elif self.clicks == 1:
            self.win_points.append (event.xdata)
            for ax,vl in zip (self.fig.axes, self.vlines):
                ax.lines.remove (vl)
            xmin, xmax = min (self.win_points), max (self.win_points)
            self.complete (xmin,xmax)
        self.clicks += 1

class Iverplot_window (object):
    """
    Iverplot_window---main Iverplot GUI object

    Parameters
    -----------

    Notes
    ------

    """
    def __init__ (self):
        self.builder = gtk.Builder ()
        self.builder.add_from_file ('iverplot.glade')
        self.builder.connect_signals (self)
        self.window = self.builder.get_object ('main_window')

        # add matplotlib figure canvas
        w,h = self.window.get_size ()
        self.fig = Figure (figsize=(6,4))
        self.canvas = FigureCanvas (self.fig)  # a gtk.DrawingArea
        self.canvas.set_size_request (w-150,-1)

        vbox = gtk.VBox()
        toolbar = NavigationToolbar (self.canvas, self.window)
        vbox.pack_start (self.canvas, True, True)
        vbox.pack_start (toolbar, False, False)

        # a little hacky for packing hpane with figure canvas first then tool
        # bar---not sure if glade is to blame---first, remove tool_vbox then
        # repack
        plot_hpaned = self.builder.get_object ('plot_hpaned')
        self.tool_vbox = self.builder.get_object ('tool_vbox')
        plot_hpaned.remove (self.tool_vbox)

        #plot_hpaned.pack1 (self.canvas, resize=True, shrink=False)
        plot_hpaned.pack1 (vbox, resize=True, shrink=False)
        plot_hpaned.pack2 (self.tool_vbox)

        # data
        self.uvclog = None
        self.lcmlog = None

        # plot limits
        self.xlimits = [None,None]
        self.xlimits_abs = [None,None]

        # add single plot item
        self.plotdex = {}
        self.plot_items = []
        self.plot_items.append (Plot_item (self.tool_vbox,
            self.on_plot_item_selected, self.uvclog, self.lcmlog))
        self.update_subplots ()

        # setwin
        self.setwin = None

        # set some defaults
        self.cd_saveas = os.getcwd ()
        self.cd_open = os.getcwd ()

        self.window.show_all ()

    def on_setwin_clicked (self, widget):
        if self.setwin is None: 
            self.setwin = Setwin (self.canvas, self.fig, self.on_setwin_complete)

    def on_setwin_complete (self, xmin, xmax):
        self.xlimits = [xmin,xmax]
        for p in self.plot_items:
            ax = self.fig.axes[self.plotdex[p]]
            p.plot_type.set_limits (ax, *self.xlimits)
        self.canvas.draw ()
        self.setwin = None

    def on_setwin_reset (self, widget):
        if not self.setwin is None: return
        self.xlimits = [x for x in self.xlimits_abs]
        for p in self.plot_items:
            ax = self.fig.axes[self.plotdex[p]]
            p.plot_type.set_limits (ax, *self.xlimits)
        self.canvas.draw ()

    def update_subplots (self):
        self.fig.clear ()
        n = len (self.plot_items)
        for i,p in enumerate (self.plot_items):
            p.plot_type.uvclog = self.uvclog
            p.plot_type.lcmlog = self.lcmlog
            ax = self.fig.add_subplot (n,1,i+1)
            p.plot_type.plot (ax, *self.xlimits)
            self.plotdex[p] = i
        self.canvas.draw ()

    def on_plot_item_selected (self, combo, item):
        ax = self.fig.axes[self.plotdex[item]]
        item.plot_type.plot (ax, *self.xlimits)
        self.canvas.draw ()

    def update_window (self):
        while gtk.events_pending ():
            gtk.main_iteration_do (True)

    def on_add_subplot_clicked (self, widget):
        if len (self.plot_items) >= 3:
            return

        self.plot_items.append (Plot_item (self.tool_vbox,
            self.on_plot_item_selected, self.uvclog, self.lcmlog))
        self.update_subplots ()
        self.update_window ()

    def on_remove_subplot_clicked (self, widget):
        if len (self.plot_items) <= 1:
            return

        item = self.plot_items.pop (-1)
        item.remove ()
        self.update_subplots ()
        self.update_window ()

    def run_open_dialog (self):
        open_dlg = self.builder.get_object ('open_dialog')
        #open_dlg.set_current_folder (self.cd_open)
        open_dlg.set_current_folder ('/home/jeff/data/UMBS_0513/iver28/2013-06-01-dive.046')

        if len (open_dlg.list_filters ()) == 0:
            all_filter = gtk.FileFilter ()
            all_filter.set_name ('All files')
            all_filter.add_pattern ('*')
            open_dlg.add_filter (all_filter)

            lcm_filter = gtk.FileFilter ()
            lcm_filter.set_name ('LCM logs')
            lcm_filter.add_pattern ('lcmlog*')
            open_dlg.add_filter (lcm_filter)

            uvc_filter = gtk.FileFilter ()
            uvc_filter.set_name ('UVC logs')
            uvc_filter.add_pattern ('*.log')
            open_dlg.add_filter (uvc_filter)

        response = open_dlg.run ()
        fname = None
        if response == gtk.RESPONSE_OK:
            fname = open_dlg.get_filename ()
            self.cd_open = os.path.dirname (fname)

        open_dlg.hide ()
        return fname

    def on_open_lcm_clicked (self, widget):
        fname = self.run_open_dialog ()
        if fname: print 'selected', fname

    def on_open_uvc_clicked (self, widget):
        fname = self.run_open_dialog ()
        if fname: 
            print 'selected', fname
            try:
                self.uvclog = UVCLog (fname)
                self.xlimits_abs = [self.uvclog.utime[0], self.uvclog.utime[-1]]
                self.xlimits = [x for x in self.xlimits_abs]
                self.update_subplots ()
            except:
                print 'could not load correctly'

    def on_save_as_clicked (self, widget):
        save_as_dlg = self.builder.get_object ('save_as_dialog')
        save_as_dlg.set_current_folder (self.cd_saveas)
        save_as_dlg.set_current_name ('iverplot.png')

        if len (save_as_dlg.list_filters ()) == 0:
            all_filter = gtk.FileFilter ()
            all_filter.set_name ('All files')
            all_filter.add_pattern ('*')
            save_as_dlg.add_filter (all_filter)

            img_filter = gtk.FileFilter ()
            img_filter.set_name ('All images')
            img_filter.add_pattern ('*.png')
            img_filter.add_pattern ('*.jpg')
            img_filter.add_pattern ('*.pdf')
            save_as_dlg.add_filter (img_filter)

        response = save_as_dlg.run ()
        if response == gtk.RESPONSE_OK: 
            fname = save_as_dlg.get_filename ()
            self.fig.savefig (fname, dpi=self.fig.dpi)
            self.cd_saveas = os.path.dirname (fname)
        save_as_dlg.hide ()

    def on_about_clicked (self, widget):
        about = self.builder.get_object ('about_dialog')
        about.run ()
        about.hide () 

    def on_main_window_destroy (self, widget):
        gtk.main_quit ()


if __name__ == '__main__':
    win = Iverplot_window ()
    gtk.main ()

    sys.exit (0)
