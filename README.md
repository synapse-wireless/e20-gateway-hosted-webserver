# E20 Example – Gateway-Hosted Web Server

This example showcases the following products (for example, from a Synapse EK5100 kit):

* SNAP Connect E20
* 2 x SN171 Prototyping board, with RF200 module
* SN132 USB SNAP Stick

The EK5100 kit ships with this example preloaded, or you can load it manually (see [Loading This Example onto "Fresh" Hardware](#loading-this-example-onto-fresh-hardware)).

## What This Example Does

SNAPpy scripts running on the individual SNAP Nodes report button state, "button presses" (counters), and battery voltage. Python code running on the E20 Gateway implements a web server, and web browsers which connect to this web server display a table of live node data. Through that web page, you can control an LED on each SNAP Node.

Full source code for this example is available on GitHub here: 

> https://github.com/synapse-wireless/e20-gateway-hosted-webserver

The Synapse Portal IDE will allow complete embedded module development, as well as wireless sniffer capability – download the latest version here: 

> https://forums.synapse-wireless.com/showthread.php?t=9

## Running This Example

#### Connect to the E20 via WiFi
Power up the E20 and use a PC or mobile device to connect to its WiFi access point using these credentials:

> **SSID:** synapse-e20
> **Password:** synapse1

#### Visit the E20's SNAP node status page
Open a web browser on that PC or mobile device, and navigate to the E20’s URL:  http://192.168.0.1

The web page will display a simple table of wireless SNAP nodes reporting their "status". The SN171 boards run SNAPpy scripts which report status every 5 seconds, or when a button is pressed.

#### Power the SN171 boards
Connect the battery packs to the SN171 boards, and verify each pack’s switch is ON.

You should see a blinking LED on each prototyping board. Also, you’ll see both devices show up in the HTML table displayed in your web browser.

As you press the button on each board, you’ll see the press-count immediately updated in your browser. Also, the current state of each button will be reflected in real-time. In addition, the boards report their current battery level.

**NOTE** – there is an "S1SEL" jumper on each SN171 board that selects between "button is RESET" and "button is GPIO_5". Make sure the jumper is in the position labeled "GPIO5" on the silk-screen, or the demo won’t work.

There is also a checkbox on each table row that controls an LED on the corresponding SNAP Node. Click it! 

## Loading This Example onto "Fresh" Hardware

Depending on its model number, your kit may have come with this example *already preloaded* – refer to the "Kit Manual" for your particular kit. These instructions describe how to (re)load the software *if needed*.

#### Load SNAPpy scripts

First, load the SNAPpy script "demo_sn171.py" into the SN171 SNAP Nodes.

Note that Portal has to have access to these SNAPpy scripts before it can upload them into your SNAP Nodes. The scripts are located in a subdirectory named "snappyImages" in the source code tree for this example.

**Reminder** – you can manually copy all of the files in this example’s "snappyImages" directory into Portal’s "snappyImages" directory, or you can use Portal’s **Options: Set Working Directory...** feature to "aim" Portal at this example’s "snappyImages" **parent** directory.

If you choose to copy the files, be sure to copy all of them (don’t forget batmon.py, nv_settings.py, and SN173.py, which get imported by demo_sn171.py).

#### Load the various "Linux Config" files for this demo onto your E20

Look in the "e20-sys" directory, and follow the instructions in the "readme" file there. Make a note of the directory path in file e20-kit1-demo.conf and be prepared to either match it in the next step, or edit that file.

#### Install the SNAP node status web app
Copy the entire "tree" of files in the web_app directory onto your E20

NOTE – the files must go into a directory tree on the E20 such that the resulting path matches the one specified in e20-kit1-demo.conf is correct, or you must manually edit that file.

After you have placed the files, follow the instructions in the "readme" file in that directory too.

#### Now transition to the ["Running This Example"](#running-this-example) instructions earlier in this README

Either: 

**A)** Power down your E20, and then go to page 1 (where you will power it back up)

or

**B)** Just *reboot* your E20 (from the command line) and skip over the part about  "powering up the E20" when you go to page 1

## Exploring This Example

The web application is a basic Python program built with high-performance libraries, Tornado and SNAP Connect. The Javascript/HTML is kept deliberately simple for ease of understanding, although it showcases a low-latency websockets technique. This can be easily extended to REST interfaces, and other web/backend approaches to fit application requirements. More information about the software used in this example can be found in the "Software" guide (look in the same directory where you found this Quick Start).

See the README.md files in the [e20_sys](e20_sys) and [web_app](web_app) directories for more details and library dependencies.

<!--meta-tags: vvv-e20, vvv-sn171, vvv-rf200, vvv-ek5100, vvv-snapconnect, vvv-js, vvv-html, vvv-python, vvv-example-->
