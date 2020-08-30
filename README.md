Budgie Analog Clock

![Screenshot](images/clock.png?raw=true)

Add an analog clock to the Budgie Panel

This applet it still very much being worked on.  Therefore, stability is not promised.
The applet currently allows you to scale the clock through the settings.
You can manually change colors of the clock outline, face, and hands through dconf.

This requires python3-svgwrite to be installed:
* sudo apt install python3-svgwrite

To install:
./install.sh

This will:
* check for python3-svgwrite and install if missing
* copy the plugin files to /usr/lib/budgie-desktop/plugins
* compile the schema
