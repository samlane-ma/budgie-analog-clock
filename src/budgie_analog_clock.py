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

""" Some "constants":
    Clock is drawn at 100x100 px resolution, with a center at 50,50 and 
    then scaled to fit panel, but these can be played around with to fine
    tune the clocks appearance.
"""
IMAGE_SIZE         = 100  # 100 default
MAXIMUM_SIZE       = 200  # 200 default
MINIMUM_SIZE       =  22  #  22 default
X_CENTER           =  50  #  50 default
Y_CENTER           =  50  #  50 default
CLOCK_RADIUS       =  46  #  46 default
HOUR_HAND_LENGTH   =  28  #  28 default
MINUTE_HAND_LENGTH =  38  #  38 default
FRAME_THICKNESS    =   5  #   5 default
HAND_THICKNESS     =   5  #   5 default
MARKING_THICKNESS  =   3  #   3 default
MARKING_LENGTH     =   7  #   7 default
UPDATE_INTERVAL    =   5  #   5 default (in seconds)
FORCE_REDRAW       =  -1  # This is just to clarify why -1 is used in the code

app_settings = Gio.Settings.new("com.github.samlane-ma.budgie-analog-clock")
path = "com.solus-project.budgie-panel"

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

        self.label_text = ["", "Clock Size (px)","Frame Color","Hands Color",
                           "Face Color","Transparent face","","Show hour marks"]
        self.setting_name = ["clock-outline","clock-hands","clock-face"]

        for n in range(8):
            label = Gtk.Label()
            label.set_text(self.label_text[n])
            label.set_halign(Gtk.Align.START)
            label.set_valign(Gtk.Align.CENTER)
            self.attach(label, 0, n, 1, 1)

        spin_clock_size_adj = Gtk.Adjustment(value=app_settings.get_int("clock-size"),
                                  lower=MINIMUM_SIZE, upper=MAXIMUM_SIZE, step_incr=1)
        spin_clock_size = Gtk.SpinButton()
        spin_clock_size.set_adjustment(spin_clock_size_adj)
        spin_clock_size.set_digits(0)
        self.attach(spin_clock_size, 1, 1, 1, 1)

        self.colorbuttons = []
        for n in range(3):
            load_color = app_settings.get_string(self.setting_name[n])
            color = Gdk.RGBA()
            if load_color == "none":
                color.parse("rgba(0,0,0,0)")
            else:
                color.parse(load_color)
            button = Gtk.ColorButton.new_with_rgba(color)
            button.connect("color_set",self.on_color_changed,self.setting_name[n])
            self.colorbuttons.append(button)
            self.attach(self.colorbuttons[n], 1, n+2, 1, 1)

        button_set_transparent = Gtk.Button.new_with_label("Set")
        button_set_transparent.connect("clicked",self.on_set_transparent)
        self.attach(button_set_transparent, 1, 5, 1, 1)
        switch_markings = Gtk.Switch()
        switch_markings.set_halign(Gtk.Align.END)
        self.attach(switch_markings, 1, 7, 1, 1)

        app_settings.bind("clock-size",spin_clock_size,"value",Gio.SettingsBindFlags.DEFAULT)
        app_settings.bind("draw-marks",switch_markings,"active",Gio.SettingsBindFlags.DEFAULT)

        self.show_all()

    def on_set_transparent(self, button):
        self.colorbuttons[2].set_alpha(0)
        app_settings.set_string("clock-face","none")

    def on_color_changed(self, button, clock_part):
        color = button.get_color()
        hex_code = "#{:02x}{:02x}{:02x}".format(int(color.red/256),
                                                int(color.green/256),
                                                int(color.blue/256))
        app_settings.set_string(clock_part, hex_code)


class BudgieAnalogClockApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """
    manager = None

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)

        self.uuid = uuid
        self.keep_running = True

        user = os.environ["USER"]
        self.tmp = os.path.join("/tmp/", user + "_panel_analog_clock.svg")
        self.max_size = MAXIMUM_SIZE

        self.load_settings()

        self.box = Gtk.Box()
        self.add(self.box)
        self.clock_image = Gtk.Image()
        self.box.add(self.clock_image)
        self.show_all()
        app_settings.connect("changed",self.on_settings_change)
        GLib.timeout_add_seconds(UPDATE_INTERVAL, self.update_time)

        # This triggers the applet to shut down when removed from the panel
        # It needs a slight delay to work correctly
        GLib.timeout_add_seconds(1, self.watch_applet, str(uuid))
 
    def find_applet (self, str_uuid, applets):
        for find_uuid in applets:
            if find_uuid == self.uuid:
                return True
        return False 

    def watch_applet (self, str_uuid):
        applets = []
        panel_settings = Gio.Settings(path);
        allpanels_list = panel_settings.get_strv("panels");
        for p in allpanels_list:
            panelpath = "/com/solus-project/budgie-panel/panels/"+"{"+ p+ "}/"
            self.currpanelsubject_settings = Gio.Settings.new_with_path(path + ".panel", panelpath)
            applets =self.currpanelsubject_settings.get_strv("applets")
            if self.find_applet(str_uuid, applets):
                # Need this signal id to disconnect it on quit
                self.signal_id = self.currpanelsubject_settings.connect(
                              "changed::applets", self.is_applet_running)
        return False

    def is_applet_running (self, arg1, arg2):
        applets =self.currpanelsubject_settings.get_strv("applets")
        if not self.find_applet(self.uuid, applets):
            # Disconnect the signal
            self.currpanelsubject_settings.disconnect(self.signal_id)
            self.keep_running = False 

    def do_panel_position_changed(self,position):
        if position == Budgie.PanelPosition.TOP or position == Budgie.PanelPosition.BOTTOM:
            self.box.set_orientation(Gtk.Orientation.HORIZONTAL)
        else:
            self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.update_clock()

    def do_panel_size_changed(self,panel_size,icon_size,small_icon_size):
        # Keeps the clock smaller than panel, but no smaller than MINIMUM_SIZE
        self.max_size = panel_size - 6
        if self.max_size < MINIMUM_SIZE:
            self.max_size = MINIMUM_SIZE
        current_size = app_settings.get_int("clock-size")
        # Don't let the clock get bigger than the Budgie Panel
        if current_size > self.max_size:
            self.clock_scale = self.max_size
        self.update_clock()

    def validate_settings(self):
        """ Reset invalid colors to defaults - "none" is a valid color name.
            Invalid settings (hopefully) should really only ever occur if
            the dconf values are manually set to something wrong
        """
        setting_name = ["clock-hands", "clock-outline", "clock-face"]
        default_color = ["#000000", "#000000", "#FFFFFF"]
        for n in range(3):
            testcolor = Gdk.RGBA()
            colorname = app_settings.get_string(setting_name[n])
            if (colorname != "none") and (not testcolor.parse(colorname)):
                app_settings.set_string(setting_name[n],default_color[n])

    def on_settings_change(self, arg1, arg2):
        self.load_settings()
        self.update_clock()

    def load_settings(self):
        self.clock_scale = app_settings.get_int("clock-size")
        if self.clock_scale > self.max_size:
            self.clock_scale = self.max_size
        self.hands_color = app_settings.get_string("clock-hands")
        self.line_color = app_settings.get_string("clock-outline")
        self.fill_color = app_settings.get_string("clock-face")
        self.draw_hour_marks = app_settings.get_boolean("draw-marks")

    def update_clock(self):
        self.old_minute = FORCE_REDRAW
        self.validate_settings()
        self.update_time()

    def update_time(self):
        self.current_time = datetime.datetime.now()
        # Don't redraw unless time (minute) has changed
        if self.current_time.minute != self.old_minute:
            """ In the rare instance where the time zone is changed while applet
                is running, tzset will ensure the clock recognizes the change.
                Possibly may also be needed to recognize daylight savings change?
            """
            time.tzset()
            self.old_minute = self.current_time.minute
            self.create_clock_image(self.current_time.hour, self.current_time.minute)
            GObject.idle_add(self.load_new_image)
        return self.keep_running

    def load_new_image(self):
        self.clock_image.set_tooltip_text(self.current_time.strftime("%a %x"))
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.tmp, self.clock_scale,
                                                              self.clock_scale, True)
        self.clock_image.set_from_pixbuf(self.pixbuf)

    def create_clock_image (self, hours, mins):
        # If time is PM
        if hours > 12:
            hours -= 12
        # Treat hour hand like minute hand so it can be between hour markings
        hours = hours * 5 + (mins / 12)
        dwg = svgwrite.Drawing(self.tmp, (IMAGE_SIZE, IMAGE_SIZE))
        # Draw an outside circle for the clock, and a small circle at the base of the hands
        dwg.add(dwg.circle((X_CENTER, Y_CENTER), CLOCK_RADIUS, fill=self.fill_color,
                            stroke=self.line_color, stroke_width=FRAME_THICKNESS))
        dwg.add(dwg.circle((X_CENTER, Y_CENTER), 3, 
                            stroke=self.hands_color, fill=self.hands_color, stroke_width=3))

        # We are going to add hour markings around the outside edge of the clock
        if self.draw_hour_marks:
            for markings in range(12):
                mark_x_start, mark_y_start = self.get_clock_hand_xy(markings * 5, CLOCK_RADIUS)
                mark_x_end, mark_y_end = self.get_clock_hand_xy(markings * 5, CLOCK_RADIUS - MARKING_LENGTH)
                dwg.add(dwg.line((mark_x_start, mark_y_start), (mark_x_end, mark_y_end),
                                  stroke=self.line_color, stroke_width=MARKING_THICKNESS))

        # Draw the minute and hour hands from the center to the calculated points
        hour_hand_x, hour_hand_y = self.get_clock_hand_xy (hours, HOUR_HAND_LENGTH)
        minute_hand_x, minute_hand_y = self.get_clock_hand_xy (mins, MINUTE_HAND_LENGTH)
        dwg.add(dwg.line((X_CENTER,Y_CENTER), (hour_hand_x,hour_hand_y),
                          stroke=self.hands_color, stroke_width=HAND_THICKNESS))
        dwg.add(dwg.line((X_CENTER,Y_CENTER), (minute_hand_x,minute_hand_y),
                          stroke=self.hands_color, stroke_width=HAND_THICKNESS))
        dwg.save()

    def get_clock_hand_xy (self, hand_position,length):
        """ This fixes the issue that 0 degrees on a cirlce is actually 3:00
            on a clock, not 12:00 -essentially rotates the hands 90 degrees
        """
        hand_position -= 15
        if hand_position < 0:
            hand_position += 60
        # And here is how we determine the x and y coordinate to draw to
        radians = (hand_position * (pi * 2) / 60)
        x_position = round (X_CENTER + length * cos(radians))
        y_position = round (Y_CENTER + length * sin(radians))
        return x_position, y_position

    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True

    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return BudgieAnalogClockSettings(self.get_applet_settings(self.uuid))
