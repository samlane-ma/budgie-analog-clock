#Budgie Analog Clock

![Screenshot](images/clock.png?raw=true)

##Add an analog clock to the Budgie Panel

This applet it still very much being worked on.  Therefore, stability is not promised.
The applet currently allows you to scale the clock through the settings.
For the time being, you can manually change colors of the clock outline, face, and hands through dconf.

Current issues:
* If you have a light panel, the clock will be hard/impossible to see unless you change the clock colors
* Ihe clock can be scaled larger than the panel size.  This will cause the panel to overlap windows, unless you increase the panel size as well.

This requires python3-svgwrite to be installed:
* sudo apt install python3-svgwrite

To install:
./install.sh

This will:
* check for python3-svgwrite and install if missing
* copy the plugin files to /usr/lib/budgie-desktop/plugins
* compile the schema
