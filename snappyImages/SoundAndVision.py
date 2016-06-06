# Copyright (C) 2016 Synapse Wireless, Inc.
# Subject to your agreement of the disclaimer set forth below, permission is given by Synapse Wireless, Inc. ("Synapse") to you to freely modify, redistribute or include this SNAPpy code in any program. The purpose of this code is to help you understand and learn about SNAPpy by code examples.
# BY USING ALL OR ANY PORTION OF THIS SNAPPY CODE, YOU ACCEPT AND AGREE TO THE BELOW DISCLAIMER. If you do not accept or agree to the below disclaimer, then you may not use, modify, or distribute this SNAPpy code.
# THE CODE IS PROVIDED UNDER THIS LICENSE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, WITHOUT LIMITATION, WARRANTIES THAT THE COVERED CODE IS FREE OF DEFECTS, MERCHANTABLE, FIT FOR A PARTICULAR PURPOSE OR NON-INFRINGING. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE COVERED CODE IS WITH YOU. SHOULD ANY COVERED CODE PROVE DEFECTIVE IN ANY RESPECT, YOU (NOT THE INITIAL DEVELOPER OR ANY OTHER CONTRIBUTOR) ASSUME THE COST OF ANY NECESSARY SERVICING, REPAIR OR CORRECTION. UNDER NO CIRCUMSTANCES WILL SYNAPSE BE LIABLE TO YOU, OR ANY OTHER PERSON OR ENTITY, FOR ANY LOSS OF USE, REVENUE OR PROFIT, LOST OR DAMAGED DATA, OR OTHER COMMERCIAL OR ECONOMIC LOSS OR FOR ANY DAMAGES WHATSOEVER RELATED TO YOUR USE OR RELIANCE UPON THE SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES OR IF SUCH DAMAGES ARE FORESEEABLE. THIS DISCLAIMER OF WARRANTY AND LIABILITY CONSTITUTES AN ESSENTIAL PART OF THIS LICENSE. NO USE OF ANY COVERED CODE IS AUTHORIZED HEREUNDER EXCEPT UNDER THIS DISCLAIMER.

"""
SoundAndVision.py

This program demonstrates the ability of SNAP nodes to communicate with each other and react
to sensor readings, even when those readings are performed by a different node.

The assumption for this script is that one node will be connected to a thermistor (GPIO_18/GPIO_B7)
and a piezo (GPIO_9/GPIO_G3), and another node will be connected to a photo cell (GPIO_11/GPIO_A4)
and three LEDs: Red (GPIO_0/GPIO_D3), Amber (GPIO_4/GPIO_C2) and Green (GPIO_6/GPIO_B3).

The LEDs on the second unit will change state based on the temperature of the thermistor on
the first unit. (Warmer temperatures are red. Colder temperatures are green.) The piezo on
the first unit will beep for different durations depending on the light levels detected by
the second unit. (The darker it is, the shorter the beeps will be. Total darkness is silence.)

Additionally, an LED on GPIO_1/GPIO_D2 provides a heartbeat indicating that the node has power,
and an LED on GPIO_2/GPIO_D1 indicates that another node with this script is powered in range.

Use the associated functions to adjust the threshold levels to suit your purposes.
"""

from synapse.platforms import *

if platform[0:2] == 'RF':
    LED_1 = GPIO_1
    LED_2 = GPIO_2
    LED_RED = GPIO_0
    LED_AMBER = GPIO_4
    LED_GREEN = GPIO_6
    PIEZO = GPIO_9
    DRIVE_LOW = (GPIO_3, GPIO_5)
    DRIVE_HIGH = GPIO_12
    THERMISTOR = GPIO_18
    PHOTO_CELL = GPIO_11
else:
    LED_1 = GPIO_D2
    LED_2 = GPIO_D1
    LED_RED = GPIO_D3
    LED_AMBER = GPIO_C2
    LED_GREEN = GPIO_B3
    PIEZO = GPIO_G3
    DRIVE_LOW = (GPIO_C1, GPIO_C3)
    DRIVE_HIGH = GPIO_B4
    THERMISTOR = GPIO_B7
    PHOTO_CELL = GPIO_A4

OUTPUTS = (LED_1, LED_2, LED_RED, LED_AMBER, LED_GREEN, PIEZO, DRIVE_HIGH, DRIVE_LOW[0], DRIVE_LOW[1])

THERMISTOR_ADC = 7
PHOTO_CELL_ADC = 0

GREEN_THRESHOLD_NV = 15
AMBER_THRESHOLD_NV = 50
RED_THRESHOLD_NV = 100
SHORT_THRESHOLD_NV = 138
MEDIUM_THRESHOLD_NV = 139
LONG_THRESHOLD_NV = 140

DEFAULT_GREEN_THRESHOLD = 15
DEFAULT_AMBER_THRESHOLD = 50
DEFAULT_RED_THRESHOLD = 100
DEFAULT_SHORT_THRESHOLD = 1000
DEFAULT_MEDIUM_THRESHOLD = 500
DEFAULT_LONG_THRESHOLD = 100

LONG_BEEP = 375
MEDIUM_BEEP = 200
SHORT_BEEP = 50
LIGHT_THRESHOLD = 50

light_level = 0  #  Light level measured after crossing the threshold
base_thermistor_level = 0  # Initial thermistor reading to use as a temperature baseline
timer_count = 0  # used by timer hooks to monitor what's going on


@setHook(HOOK_STARTUP)
def _onStartup():
    global base_thermistor_level
    
    # Initialize values for the appropriate NV parameters, in case they've never been set.
    _check_default_thresholds()
    
    # Set all those pins for LEDs and buzzers as outputs, driven low
    for pin in OUTPUTS:
        setPinDir(pin, True)
        writePin(pin, False)
    # Now, go back and set that DRIVE_HIGH pin as high, as it will be VCC for the photo cell
    writePin(DRIVE_HIGH, True)
    
    # Take initial temperature reading to use as a baseline.
    base_thermistor_level = get_thermistor()
    
    # FLASH LEDs on boot
    engage_green()
    engage_amber()
    engage_red()

@setHook(HOOK_100MS)
def _every_decisecond(tick):
    global timer_count 
    global light_level
    timer_count += 1
    timer_count %= 5
    if timer_count == 1:
        # The heartbeat counter
        pulsePin(LED_1, 250, True)  # My own heartbeat
        mcastRpc(1, 1, 'can_you_hear_me')
    elif timer_count == 2:
        # Read the photo cell (if so equipped)
        photo_cell_value = get_photo_cell()
        # Send the value, and let the receiving node decide what to do with it
        if photo_cell_value > (light_level + LIGHT_THRESHOLD) or photo_cell_value < (light_level - LIGHT_THRESHOLD):
            mcastRpc(1, 1, 'report_photo_cell', photo_cell_value)
            light_level = photo_cell_value
    elif timer_count == 3:
        # Read the thermistor (if so equipped)
        thermistor_value = get_thermistor()
        # Decide how the receiving node should respond, and send that command
        if thermistor_value < (base_thermistor_level - loadNvParam(GREEN_THRESHOLD_NV)):
            mcastRpc(1, 1, 'engage_green')
        if thermistor_value < (base_thermistor_level - loadNvParam(AMBER_THRESHOLD_NV)):
            mcastRpc(1, 1, 'engage_amber')
        if thermistor_value < (base_thermistor_level - loadNvParam(RED_THRESHOLD_NV)):
            mcastRpc(1, 1, 'engage_red')

def get_thermistor():
    return readAdc(THERMISTOR_ADC)

def get_photo_cell():
    return readAdc(PHOTO_CELL_ADC)

def can_you_hear_me():
    # This provides a heartbeat indicating that another node is awake and in range
    pulsePin(LED_2, 250, True)

def report_photo_cell(photo_cell_value):
    # The other node will send its photo cell reading here.
    # We will parse what to do with it, based on our NV parameters.
    if photo_cell_value < loadNvParam(LONG_THRESHOLD_NV):
        pulsePin(PIEZO, LONG_BEEP, True)
    elif photo_cell_value < loadNvParam(MEDIUM_THRESHOLD_NV):
        pulsePin(PIEZO, MEDIUM_BEEP, True)
    elif photo_cell_value < loadNvParam(SHORT_THRESHOLD_NV):
        pulsePin(PIEZO, SHORT_BEEP, True)
    # The else condition is to do nothing.

# The three "engage_{color}" functions are invoked by the other node, which decides 
# which to invoke based on a comparison of its NV parameters and the thermistor value.
def engage_green():
    # Flash the green LED for just over a half second.
    # This can be invoked about every half second, so it will seem solid
    # when it is repeatedly invoked.
    pulsePin(LED_GREEN, 550, True)

def engage_amber():
    # Flash the green LED for just over a half second.
    # This can be invoked about every half second, so it will seem solid
    # when it is repeatedly invoked.
    pulsePin(LED_AMBER, 550, True)

def engage_red():
    # Flash the green LED for just over a half second.
    # This can be invoked about every half second, so it will seem solid
    # when it is repeatedly invoked.
    pulsePin(LED_RED, 550, True)

def _check_default_thresholds():
    # Check to see whether any of the threshold values in NV parameters are not integers.
    # If all six are integers, we have to assume that they have been set explicitly.
    # Resetting factory parameters on a node sets all six to None.
    if type(loadNvParam(GREEN_THRESHOLD_NV)) != 1 or \
        type(loadNvParam(AMBER_THRESHOLD_NV)) != 1 or \
        type(loadNvParam(RED_THRESHOLD_NV)) != 1 or \
        type(loadNvParam(SHORT_THRESHOLD_NV)) != 1 or \
        type(loadNvParam(MEDIUM_THRESHOLD_NV)) != 1 or \
        type(loadNvParam(LONG_THRESHOLD_NV)) != 1 :
        # (At least) One of the parameters is not an integer (type == 1)
        default_thresholds()

def default_thresholds():
    # Set threshold levels to their defaults
    saveNvParam(GREEN_THRESHOLD_NV, DEFAULT_GREEN_THRESHOLD)
    saveNvParam(AMBER_THRESHOLD_NV, DEFAULT_AMBER_THRESHOLD)
    saveNvParam(RED_THRESHOLD_NV, DEFAULT_RED_THRESHOLD)
    saveNvParam(SHORT_THRESHOLD_NV, DEFAULT_SHORT_THRESHOLD)
    saveNvParam(MEDIUM_THRESHOLD_NV, DEFAULT_MEDIUM_THRESHOLD)
    saveNvParam(LONG_THRESHOLD_NV, DEFAULT_LONG_THRESHOLD)
    return "Thresholds defaulted."

def set_green_threshold(green_threshold):
    if type(green_threshold) != 1:  # Integer
        return "Invalid Green Threshold Value"
    old = str(loadNvParam(GREEN_THRESHOLD_NV))
    saveNvParam(GREEN_THRESHOLD_NV, green_threshold)
    return "Green threshold changed from " + old + " to " + str(green_threshold)

def set_amber_threshold(amber_threshold):
    if type(amber_threshold) != 1:  # Integer
        return "Invalid Amber Threshold Value"
    old = str(loadNvParam(AMBER_THRESHOLD_NV))
    saveNvParam(AMBER_THRESHOLD_NV, amber_threshold)
    return "Amber threshold changed from " + old + " to " + str(amber_threshold)

def set_red_threshold(red_threshold):
    if type(red_threshold) != 1:  # Integer
        return "Invalid Red Threshold Value"
    old = str(loadNvParam(RED_THRESHOLD_NV))
    saveNvParam(RED_THRESHOLD_NV, red_threshold)
    return "Red threshold changed from " + old + " to " + str(red_threshold)

def set_short_threshold(short_threshold):
    if type(short_threshold) != 1:  # Integer
        return "Invalid Short Threshold Value"
    old = str(loadNvParam(SHORT_THRESHOLD_NV))
    saveNvParam(SHORT_THRESHOLD_NV, short_threshold)
    return "Short threshold changed from " + old + " to " + str(short_threshold)

def set_medium_threshold(medium_threshold):
    if type(medium_threshold) != 1:  # Integer
        return "Invalid Medium Threshold Value"
    old = str(loadNvParam(MEDIUM_THRESHOLD_NV))
    saveNvParam(MEDIUM_THRESHOLD_NV, medium_threshold)
    return "Medium threshold changed from " + old + " to " + str(medium_threshold)

def set_long_threshold(long_threshold):
    if type(long_threshold) != 1:  # Integer
        return "Invalid Long Threshold Value"
    old = str(loadNvParam(LONG_THRESHOLD_NV))
    saveNvParam(LONG_THRESHOLD_NV, long_threshold)
    return "Long threshold changed from " + old + " to " + str(long_threshold)

def get_thresholds_color():
    red = str(loadNvParam(RED_THRESHOLD_NV))
    amber = str(loadNvParam(AMBER_THRESHOLD_NV))
    green = str(loadNvParam(GREEN_THRESHOLD_NV))
    return_value = "Red: " + red + " | Amber: " + amber + " | Green: " + green
    return return_value

def get_thresholds_tone():
    short = str(loadNvParam(SHORT_THRESHOLD_NV))
    medium = str(loadNvParam(MEDIUM_THRESHOLD_NV))
    long = str(loadNvParam(LONG_THRESHOLD_NV))
    return_value = "Short: " + short + " | Medium: " + medium + " | Long: " + long
    return return_value