import gi.repository
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, GdkPixbuf, GLib, Gio, Gdk
import time
import os
import svgwrite
import datetime
from math import sin, cos, pi

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

X_CENTER = 50
Y_CENTER = 50
CLOCK_RADIUS = 37
HOUR_HAND_LENGTH = 21
MINUTE_HAND_LENGTH = 31

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

        self.label_colors = ["Clock Color", "Hands Color", "Face Color"]
        self.setting_name = ["clock-outline", "clock-hands", "clock-face"]

        self.blank_label = Gtk.Label("")
        self.blank_label.set_halign(Gtk.Align.START)
        self.attach(self.blank_label, 0, 0, 2, 1)
        self.label_size = Gtk.Label("Clock Size (px)")
        self.label_size.set_halign(Gtk.Align.START)
        self.label_size.set_valign(Gtk.Align.CENTER)
        self.attach(self.label_size, 0, 1, 1, 1)

        self.adj = Gtk.Adjustment(value=app_settings.get_int("clock-size"),
                                  lower=10, upper=100, step_incr=1)
        self.spin_clock_size = Gtk.SpinButton()
        self.spin_clock_size.set_adjustment(self.adj)
        self.spin_clock_size.set_digits(0)
        self.spin_clock_size.connect("changed",self.on_clock_size_changed)
        self.attach(self.spin_clock_size, 1, 1, 1, 1)

        self.colorbuttons = []

        for n in range(3):
            colorlabel = Gtk.Label(self.label_colors[n])
            colorlabel.set_halign(Gtk.Align.START)
            load_color = app_settings.get_string(self.setting_name[n])
            color = Gdk.RGBA()
            if load_color == "none":
                color.parse("rgba(0,0,0,0)")
            else:
                color.parse(load_color)
            button = Gtk.ColorButton.new_with_rgba(color)
            button.connect("color_set",self.on_color_changed,self.setting_name[n])
            self.colorbuttons.append(button)
            self.attach(colorlabel, 0, n+2, 1, 1)
            self.attach(self.colorbuttons[n], 1, n+2, 1, 1)

        self.label_reset = Gtk.Label("Reset clock face \nto transparent")
        self.label_reset.set_halign(Gtk.Align.START)
        self.button_reset_face = Gtk.Button("Reset")
        self.button_reset_face.connect("clicked",self.on_reset_face)
        self.attach(self.label_reset, 0, 5, 1, 1)
        self.attach(self.button_reset_face, 1, 5, 1, 1)

        self.show_all()

    def on_reset_face(self, button):
        app_settings.set_string("clock-face","none")

    def on_clock_size_changed(self, spinner):
        app_settings.set_int("clock-size",spinner.get_value())

    def on_color_changed (self, button, clock_part):
        color = button.get_color()
        hex_code = "#{:02x}{:02x}{:02x}".format(int(color.red/256),int(color.green/256),int(color.blue/256))
        app_settings.set_string(clock_part, hex_code)


class BudgieAnalogClockApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)

        self.uuid = uuid

        user = os.environ["USER"]
        self.tmp = os.path.join("/tmp", user + "_panel_analog_clock.svg")

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.box)
        self.clock_image = Gtk.Image()
        self.validate_settings()
        self.update_settings("","")
        self.update_time()
        self.show_all()

        app_settings.connect("changed",self.update_settings)
        GLib.timeout_add_seconds(5, self.update_time)

    def validate_settings(self):
        # Reset invalid colors to defaults - "none" is a valid color name
        setting_name = ["clock-hands", "clock-outline", "clock-face"]
        default_color = ["#000000", "#000000", "#FFFFFF"]
        for n in range(3):
            testcolor = Gdk.RGBA()
            colorname = app_settings.get_string(setting_name[n])
            if (colorname != "none") and (not testcolor.parse(colorname)):
                app_settings.set_string(setting_name[n],default_color[n])

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
        if self.current_time.minute != self.old_minute:
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
        # If time is PM
        if hours > 12:
            hours -= 12
        # Treat hour hand like minute hand so it can be between hour markings
        hours = hours * 5 + (mins / 12)

        dwg = svgwrite.Drawing(self.tmp, (100, 100))
        # Draw an outside circle for the clock, and a small circle at the base of the hands
        dwg.add(dwg.circle((X_CENTER, Y_CENTER), CLOCK_RADIUS, 
                           fill=self.fill_color, stroke=self.line_color, stroke_width=4))
        dwg.add(dwg.circle((X_CENTER, Y_CENTER), 3, 
                           stroke=self.hands_color, stroke_width=3))

        # TODO: Maybe make the markings optional
        # We are going to add hour markings around the outside edge of the clock
        for markings in range(12):
            mark_rad = pi * 2 - (markings * (pi * 2) / 12)
            mark_x = round (X_CENTER + (CLOCK_RADIUS - 3) * cos(mark_rad))
            mark_y = round (X_CENTER + (CLOCK_RADIUS - 3)  * sin(mark_rad))
            dwg.add(dwg.circle((mark_x,mark_y), 2, fill=self.line_color))

        # Draw the minute and hour hands from the center to the calculated points
        hour_hand_x, hour_hand_y = self.get_clock_hand_xy (hours, HOUR_HAND_LENGTH)
        minute_hand_x, minute_hand_y = self.get_clock_hand_xy (mins, MINUTE_HAND_LENGTH)
        dwg.add(dwg.line((X_CENTER,Y_CENTER), (hour_hand_x,hour_hand_y), stroke=self.hands_color, stroke_width=6))
        dwg.add(dwg.line((X_CENTER,Y_CENTER), (minute_hand_x,minute_hand_y), stroke=self.hands_color, stroke_width=6))
        dwg.save()

    def get_clock_hand_xy (self, hand_position, LENGTH):
        """ This fixes the issue that 0 degrees on a cirlce is actually 3:00
            on a clock, not 12:00 -essentially rotates the hands 90 degrees
        """
        if hand_position < 15:
            hand_position = hand_position + 60
        hand_position = (hand_position - 15)
        # And here is how we determine the x and y coordinate to draw to
        radians = (hand_position * (pi * 2) / 60)
        x_position = round (X_CENTER + LENGTH * cos(radians))
        y_position = round (Y_CENTER + LENGTH * sin(radians))
        return x_position, y_position

    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True

    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return BudgieAnalogClockSettings(self.get_applet_settings(self.uuid))
