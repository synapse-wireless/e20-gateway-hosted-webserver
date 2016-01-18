# E20 Example Linux Configuration Files

This directory contains files needed to enable demo on the E20.
(see E20 User Guide for details of these changes)

## Files changed/added to enable WiFi AP mode

**Note**: This sets the WiFi AP mode SSID to "synapse-e20" with the password "synapse1"

    /etc/network/interfaces
    /etc/rc2.d/S10wifiAP

Make sureS10wifiAP is executable, or it won't have any effect.
(ex. `chmod 777 /etc/rc2.d/S10wifiAP`)

## File to start demo app at boot, as service

    /etc/init/e20-kit1-demo.conf

This file assumes/requires that directory tree e20-kit1-demo resides in `/home/snap`. If you pulled the example source code directly from GitHub, you may need to move the files, or change the path to app_server.py in file e20-kit1-demo.conf.
