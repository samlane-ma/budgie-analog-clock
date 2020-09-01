# Budgie Analog Clock

![Screenshot](images/clock.png?raw=true)

## Add an analog clock to the Budgie Panel

This applet it still very much being worked on.  Therefore, stability is not promised.
The applet currently allows you to scale the clock and change colors through the settings.

Current issues:
* To prevent panel overlap issues, if you decrease the panel size, the clock will decrease in size if necessary to keep it smaller than the panel.  If you then increase the panel size, you will need to re-adjust the clock size if you want it to be larger again.  It doesn't "remember" the old setting.

This requires python3-svgwrite to be installed:
(if you have Budgie Clockworks, you have this)
* sudo apt install python3-svgwrite

To install:
./install.sh

This will:
* check for python3-svgwrite and install if missing
* copy the plugin files to /usr/lib/budgie-desktop/plugins
* compile the schema
