"""
UVC log parsing utilities and UVCLog object definition.
"""

from time import strptime, mktime

from numpy import asarray, zeros
from pandas import read_csv

from perls.BotCore import BotGPSLinearize

from .. import utils

dtor = utils.units.degree_to_radian
rtod = utils.units.radian_to_degree

def uvc_datetime_to_utime (tods, dates):
    utime = []
    for (tod, date) in zip (tods, dates):
        tod_args = tod.split ('.') 
        tod_secs = tod_args[0]
        tod_frac = tod_args[1]
        time_str = date + " " + tod_secs
        time_t = strptime (time_str, "%m/%d/%Y %H:%M:%S")
        utime.append (utils.units.second_to_microsecond (mktime (time_t) + float (tod_frac)*1e-2))
    return asarray (utime)

class UVCLog (object):
    """
    UVC log object---contains lists of all uvc log entries for a given mission
    log.

    Parameters
    -----------
    logpath : path to uvc logfile

    for full list of UVC log attributes, see Ocean-Server documentation
    """
    def __init__ (self, logpath, orglat_deg=None, orglon_deg=None):
        self._new_from_file (logpath)

        if not orglat_deg or not orglon_deg:
            self.orglat, self.orglon = self.latitude[0], self.longitude[0]
            orglat_deg, orglon_deg = rtod (self.latitude[0]), rtod (self.longitude[0])
        else:
            self.orglat, self.orglon = dtor (orglat_deg), dtor (orglon_deg)

        # bot does not use NED so we switch the return tuple y,x below
        llxy = BotGPSLinearize (orglat_deg, orglon_deg)
        self.x = zeros (self.latitude.shape) 
        self.y = zeros (self.longitude.shape)
        for i, (lat,lon) in enumerate (zip (self.latitude, self.longitude)):
           self.y[i],self.x[i] = llxy.to_xy (rtod (lat), rtod (lon))

    def _new_from_file (self, logpath):
        df = read_csv (logpath, sep=';')
        data = df.to_records ()

        # time/date
        time_of_day = data['Time']
        date = data['Date']

        self.utime = uvc_datetime_to_utime (time_of_day, date)
        
        self.latitude = dtor (data['Latitude'])
        self.longitude = dtor (data['Longitude'])
        self.number_of_sats = data['Number of Sats']
        self.gps_speed = data['GPS Speed (Kn)']
        self.gps_true_heading = dtor (data['GPS True Heading'])
        self.gps_magnetic_variation = dtor (data['GPS Magnetic Variation'])
        self.hdop = data['HDOP']
        self.c_magnetic_heading = dtor (data['C Magnetic Heading'])
        self.c_true_heading = dtor (data['C True Heading'])
        self.pitch_angle = dtor (data['Pitch Angle'])
        self.roll_angle = dtor (data['Roll Angle'])
        self.c_inside_temp = data['C Inside Temp (c)']
        self.dfs_depth = data['DFS Depth (m)']
        self.dtb_height = data['DTB Height (m)']
        self.total_water_colum = data['Total Water Column (m)']
        self.battery_percent = data['Batt Percent']
        self.power = data['Power Watts']
        self.watt_hours = data['Watt-Hours']
        self.battery_volts = data['Batt Volts']
        self.battery_amps = data['Batt Ampers']
        self.battery_state = data['Batt State']
        self.time_to_empty = data['Time to Empty']
        self.current_step = data['Current Step']
        self.dist_to_next_waypoint = data['Dist To Next (m)']
        self.next_speed = utils.units.knot_to_meter_per_second (data['Next Speed (kn)'])
        self.vehicle_speed = utils.units.knot_to_meter_per_second (data['Vehicle Speed (kn)'])
        self.motor_speed_cmd = data['Motor Speed CMD']
        self.next_heading = dtor (data['Next Heading'])
        self.next_latitude = dtor (data['Next Lat'])
        self.next_longitude = dtor (data['Next Long'])
        self.next_depth = data['Next Depth (m)']
        self.depth_goal = data['Depth Goal (m)']
        self.vehicle_state = data['Vehicle State']
        self.error_state = data['Error State']
        self.dist_to_track = data['Distance to Track (m)']
        self.fin_pitch_r = data['Fin Pitch R']
        self.fin_pitch_l = data['Fin Pitch L']
        self.fin_yaw_t = data['Fin Yaw T']
        self.fin_yaw_b = data['Fin Yaw B']
        self.yaw_goal = dtor (data['Yaw Goal'])
        self.fin_roll = data['Fin Roll']


if __name__ == '__main__':
    import sys
    import cPickle as pickle

    from perls.BotParam import BotParam
    import matplotlib.pyplot as plt

    if len (sys.argv) < 2:
        print ('usage: %s <uvc.log>' % sys.argv[0])
        sys.exit (1)

    fname = sys.argv[1]
    if '.log' in fname:
        try:
            param = BotParam (sys.argv)
            orglatlon = param.get_double_array ('site.orglatlon')
        except Exception as e:
            print 'could not find param server', e.args
            orglatlon = [None, None]
        except ValueError as e:
            print 'could not find `site.orglatlon` in param', e.args
            orglatlon = [None, None]
        uvc = UVCLog (fname, *orglatlon)
        with open ('uvclog.pkl', 'wb') as f: pickle.dump (uvc, f)
    elif '.pkl' in fname:
        with open (fname, 'rb') as f: uvc = pickle.load (f)
    else:
        print 'unrecognized file type %s' % fname
        sys.exit (1)

    fig = plt.figure ()
    ax = fig.add_subplot (111)

    ax.plot (uvc.y, uvc.x, '.-')
    ax.set_xlabel ('East---y [m]')
    ax.set_ylabel ('North---x [m]')

    ax.axis ('equal')
    ax.grid ()

    plt.show ()

    sys.exit (0)
