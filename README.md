# Budgie Analog Clock

![Screenshot](images/clock.png?raw=true)

## Add an analog clock to the Budgie Panel

This applet will add a simple analog clock on the Budgie panel. 

The applet currently allows you to:
* Change the clock size through the applet settings
* Change the color of the frame, face, and hands
* Enable or disable the hour markings on the face

The applet will respect the panel settings, and not draw a clock larger than
the Budgie Panel.  However, if the panel is resized, the clock will change size
as well, up to the clock size specified in the applet setting

This requires python3-svgwrite to be installed:

i.e. for Debian based distros
* sudo apt install python3-svgwrite

To install (for Debian/Ubuntu):

    mkdir build
    cd build
    meson --prefix=/usr --libdir=/usr/lib
    sudo ninja install

* for other distros omit libdir or specify the location of the distro library folder

This will:
* install plugin files to the Budgie Desktop plugins folder
* compile the schema
