#!/usr/bin/env bash

depend="python3-svgwrite"

dpkg -s $depend &> /dev/null  

if [ $? -ne 0 ]

    then
        echo "$depend not detected"  
        echo "Please run:   sudo apt install $depend"
    else
        echo    "$depend detected"
        sudo mkdir /usr/lib/budgie-desktop/plugins/budgie-analog-clock
        sudo cp ./BudgieAnalogClock.plugin /usr/lib/budgie-desktop/plugins/budgie-analog-clock/
        sudo cp ./budgie_analog_clock.py /usr/lib/budgie-desktop/plugins/budgie-analog-clock/
        sudo cp com.github.samlane-ma.budgie-analog-clock.gschema.xml /usr/share/glib-2.0/schemas
        sudo glib-compile-schemas /usr/share/glib-2.0/schemas
fi
