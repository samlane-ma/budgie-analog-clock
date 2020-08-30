import gi.repository
import time
import os
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, GdkPixbuf, GLib, Gio
from math import sin, cos, pi
import svgwrite
import datetime


"""
    Analog Clock Applet for the Budgie Panel
 
    Copyright © 2020 Samuel Lane
    http://github.com/samlane-ma/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
 
x_center = 50
y_center = 50
clock_rad = 37
h_length = 21
m_length = 31

app_settings = Gio.Settings.new("com.github.samlane-ma.budgie-analog-clock")
  
class BudgieAnalogClock(GObject.GObject, Budgie.Plugin):
    """ This is simply an entry point into your Budgie Applet implementation.
        Note you must always override Object, and implement Plugin.
    """
    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "BudgieAnalogClock"
    
    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)
    
    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgieAnalogClockApplet(uuid)
        

class BudgieAnalogClockSettings(Gtk.Grid):

    def __init__(self, setting):
        super().__init__()
        
        self.blank_label = Gtk.Label("")
        self.attach(self.blank_label, 0, 0, 2, 1)
        self.size_label = Gtk.Label("Clock Size (pixels)")
        self.attach(self.size_label, 0, 1, 1, 1)
        
        self.adj = Gtk.Adjustment(value=app_settings.get_int("clock-size"),lower=10, upper=100, step_incr=1, page_incr=10)
        self.spin_clock_size = Gtk.SpinButton()
        self.spin_clock_size.set_adjustment(self.adj)
        self.spin_clock_size.set_digits(0)
        self.spin_clock_size.connect("changed",self.clock_size_changed)
        self.attach(self.spin_clock_size, 1, 1, 1, 1)
        
        # IN PROGRESS 		
        # Change clock color
        # Change clock fill color  ??
        
        self.show_all()
       
    def clock_size_changed(self, spinner):
        app_settings.set_int("clock-size",spinner.get_value())


class BudgieAnalogClockApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None
    old_minute = -1
    
    def __init__(self, uuid):
        
        Budgie.Applet.__init__(self)
        
        self.uuid = uuid

        user = os.environ["USER"]
        self.tmp = os.path.join("/tmp", user + "_panel_analog_clock.svg")
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.box)
        
        self.clock_scale = app_settings.get_int("clock-size")
        self.hands_color = app_settings.get_string("clock-hands")
        self.line_color = app_settings.get_string("clock-outline")
        self.fill_color = app_settings.get_string("clock-face")
        
        self.clock_image = Gtk.Image()	
        self.update_time()
        self.show_all()
        
        app_settings.connect("changed",self.update_settings)
        
        GLib.timeout_add_seconds(5, self.update_time)
        
    def update_settings(self,arg1,arg2):
        self.old_minute = -1
        self.clock_scale = app_settings.get_int("clock-size")
        self.hands_color = app_settings.get_string("clock-hands")
        self.line_color = app_settings.get_string("clock-outline")
        self.fill_color = app_settings.get_string("clock-face")
        self.update_time()
    
    def update_time(self):
        self.current_time = datetime.datetime.now()
        # Don't redraw unless time (minute) has changed
        if self.current_time.minute != self.old_minute :
            self.old_minute = self.current_time.minute
            self.create_clock_image(self.current_time.hour, self.current_time.minute)
            self.load_new_image()
        return True

    def load_new_image(self):
        self.box.remove(self.clock_image)
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.tmp)
        self.clock_image.set_from_pixbuf(self.pixbuf.scale_simple(self.clock_scale, self.clock_scale, 2))
        self.box.add(self.clock_image)

    def create_clock_image (self, hours, mins):
        # 0 degrees in "math" circles is inconveniently 3pm on a clock, so we
        #need to shift the angle a bit- this essentially "rotates" the clock 90 deg.
        if hours > 12:
            hours -= 12    
        # Also, we need to figure hours as 1/60th instead of 1/12 of a clock face
        # so that the hour hand can be between hour markings
        h = hours * 5 + (mins / 12)
        if h < 15:
            h = h + 60
        h = (h - 15)
        # And here is how we determine the x and y coordinate to draw to
        rad_h = (h * (pi * 2) / 60)
        hx = round (x_center + h_length * cos(rad_h))
        hy = round (y_center + h_length * sin(rad_h))
        # Do the same for the minute hand
        m = mins
        if m < 15:
            m = m + 60
        m = m - 15
        rad_m = (m * (pi * 2) / 60)
        mx = round (y_center + m_length * cos(rad_m))
        my = round (x_center + m_length * sin(rad_m))

        dwg = svgwrite.Drawing(self.tmp, (100, 100))
        # Draw an outside circle for the clock, and a small circle at the base of the hands
        dwg.add(dwg.circle((x_center, y_center), clock_rad, fill=self.fill_color, stroke=self.line_color, stroke_width=6))
        dwg.add(dwg.circle((x_center, y_center), 3, stroke=self.hands_color, stroke_width=3))
        # We are going to add hour markings around the outside edge of the clock
        markings = 12
        while markings > 0:
            mark_rad = pi * 2 - (markings * (pi * 2) / 12)
            mark_x = round (x_center + (clock_rad - 3) * cos(mark_rad))
            mark_y = round (x_center + (clock_rad - 3)  * sin(mark_rad))
            dwg.add(dwg.circle((mark_x,mark_y), 2, fill=self.line_color))
            markings -= 1
        # Draw the minute and hour hands from the center to the calculated points
        dwg.add(dwg.line((x_center,y_center), (hx,hy), stroke=self.hands_color, stroke_width=6))
        dwg.add(dwg.line((x_center,y_center), (mx,my), stroke=self.hands_color, stroke_width=6))
        dwg.save()
    
    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True
        
    
    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return BudgieAnalogClockSettings(self.get_applet_settings(self.uuid))        

            
