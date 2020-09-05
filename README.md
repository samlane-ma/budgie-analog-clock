# Budgie Analog Clock

![Screenshot](images/clock.png?raw=true)

## Add an analog clock to the Budgie Panel

This applet is a work in progress.  While it so far has ben running quite well,
testing hasn't been extensive, so stability is not guaranteed.

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
* plugin files to /usr/lib/budgie-desktop/plugins
* compile the schema
* If not detected, it will inform you how to install it
