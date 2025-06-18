# https://www.nps.gov/grsm/learn/nature/firefly-flash-patterns.htm
# https://michaelweinberg.org/blog/2020/10/11/neopixel-firefly-classes/
# mods:
#    add machine.Pin import remove board
#    NeoPixel constructor
#    time.monotonic() -> time.ticks_ms()
#       delta montonic -> time.ticks_diff(t1ms,t2ms)  returns ms
#    add NEO_PIN definition
#    change how brightness is done (constructor in circuitpython, not in upython)

import time
import random
import gc

brightness = 0.1
# variables to hold the color that the LED will blink
neo_r = round(255 * brightness)
neo_g = round(200 * brightness)
neo_b = round(0 * brightness)

blue_r = round(0 * brightness)
blue_g = round(10 * brightness)
blue_b = round(255 * brightness)
white_r = round(255 * brightness)
white_g = round(255 * brightness)
white_b = round(255 * brightness)
red_r = round(255 * brightness)
red_g = round(10 * brightness)
red_b = round(0 * brightness)
green_r = round(0 * brightness)
green_g = round(255 * brightness)
green_b = round(25 * brightness)

# hanukkah_col = [[blue_r, blue_g, blue_b], [white_r, white_g, white_b]]
hanukkah_col = [[0, 0, 76], [75, 55, 55]]
christmas_col = [[red_r, red_g, red_b], [green_r, green_g, green_b]]
valentine_col = [[red_r, red_g, red_b], [white_r, white_g, white_b]]
stpat_col = [[green_r, green_g, green_b], [white_r, white_g, white_b]]

color_opts = christmas_col
# variable to hold the number of neopixels

# create the neopixel. auto_write=True avoids having to push changes (at the cost of speed,
# which probably doesn't matter here)

# sets up the bug holder list, which holds all of the bug objects


# sets up the bug class


class Bug:
    def __init__(self, type, reset_time_input, light_number):
        self.type = type
        self.reset_time_input = reset_time_input
        self.light_number = light_number


# functions to turn light on and off
def on(light_num, pixels):
    pixels[light_num] = (neo_r, neo_g, neo_b)
    pixels.write()


def off(light_num, pixels):
    pixels[light_num] = (0, 0, 0)
    pixels.write()


def selon(light_num, pixels):
    i = random.randrange(len(color_opts))
    pixels[light_num] = color_opts[i]
    pixels.write()


def brimleyi(reset_time_input, light_number, pixels):
    # calculates how much time has passed since the new zero   .. .in uPy uS
    time_from_zero = time.ticks_diff(time.ticks_ms(), reset_time_input)
    # creates the carry over reset_time variable so that it can be returned
    #  even if it is not updated in the last if statement
    reset_time = reset_time_input

    # on flash
    if 5000 <= time_from_zero <= 5500:
        selon(light_number, pixels)
    elif 15000 <= time_from_zero <= 15500:
        selon(light_number, pixels)
    # reset (includes 10 seconds after second flash - 5 on the back end and 5 on the front end)
    elif time_from_zero > 20000:
        off(light_number, pixels)
        reset_time = time.ticks_add(time.ticks_ms(), round(random.uniform(-3000, 3000)))
    # all of the off times
    else:
        off(light_number, pixels)

    return reset_time


def macdermotti(reset_time_input, light_number, pixels, debug=False):
    # calculates how much time has passed since the new zero
    time_from_zero = time.ticks_diff(time.ticks_ms(), reset_time_input)
    # creates the carry over reset_time variable so that it can be returned
    #  even if it is not updated in the last if statement
    reset_time = reset_time_input
    if debug:
        print("MacDermotti: {} {}".format(reset_time_input, time_from_zero))
    # on flash
    p = "off default"
    if 3000 <= time_from_zero <= 3500:
        selon(light_number, pixels)
        p = "one"
    elif 5000 <= time_from_zero <= 5500:
        selon(light_number, pixels)
        p = "two"
    elif 10000 <= time_from_zero <= 10500:
        selon(light_number, pixels)
        p = "three"
    elif 12000 <= time_from_zero <= 12500:
        selon(light_number, pixels)
        p = "four"
    elif time_from_zero > 14500:
        off(light_number, pixels)
        p = "off big"
        reset_time = time.ticks_add(time.ticks_ms(), round(random.uniform(-3000, 3000)))
    else:
        off(light_number, pixels)
    if debug:
        print("           : path: ", p)
        print("           : return {}".format(reset_time))

    return reset_time


def carolinus(reset_time_input, light_number, pixels):
    time_from_zero = time.ticks_diff(time.ticks_ms(), reset_time_input)
    # creates the carry over reset_time variable so that it can be returned
    #   even if it is not updated in the last if statement
    reset_time = reset_time_input

    if 0 <= time_from_zero <= 500:
        selon(light_number, pixels)
    elif 1000 <= time_from_zero <= 1500:
        selon(light_number, pixels)
    elif 2000 <= time_from_zero <= 2500:
        selon(light_number, pixels)
    elif 3000 <= time_from_zero <= 3500:
        selon(light_number, pixels)
    elif 4000 <= time_from_zero <= 4500:
        selon(light_number, pixels)
    elif 5000 <= time_from_zero <= 5500:
        selon(light_number, pixels)
    elif 6000 <= time_from_zero <= 6500:
        selon(light_number, pixels)
    elif time_from_zero >= 15:
        off(light_number, pixels)
        reset_time = time.ticks_ms()
    else:
        off(light_number, pixels)

    return reset_time


# create all of the light objects by appending a new light object to the list for each neopixel
# the first argument (random.randint(1, 3)) is used to assign a random number
#   which corresponds to one of the ff functions
# if you start adding lots of those it might be worth using a universal variable
bug_holder = None
number_of_lights = None


def initBugs(pix):
    global bug_holder
    global number_of_lights
    tnow = time.ticks_ms()
    if bug_holder is None or (len(bug_holder) != len(pix)):
        number_of_lights = len(pix)
        bug_holder = []
        for i in range(number_of_lights):
            bug_holder.append(Bug(random.randint(1, 3), tnow, i))
    else:
        for i in range(number_of_lights):
            bug_holder[i] = Bug(random.randint(1, 3), tnow, i)
    gc.collect()


def swapGRB(col):
    rv = []
    for c in col:
        rv.append([c[1], c[0], c[2]])
    return rv


def doTwinkle(pixels, twinkledata, tdur_sec=120):
    global color_opts
    color_opts = twinkledata
    initBugs(pixels)

    tend = time.ticks_add(time.ticks_ms(), tdur_sec * 1000)
    while time.ticks_ms() < tend:
        # iterates through all of the light objects in the bug_holder list
        # use the series of if statements to match the randomly
        #   assigned number to the types of fireflies

        for i in range(0, number_of_lights):
            if bug_holder[i].type == 1:
                bug_holder[i].reset_time_input = brimleyi(
                    bug_holder[i].reset_time_input, i, pixels
                )
            elif bug_holder[i].type == 2:
                bug_holder[i].reset_time_input = macdermotti(
                    bug_holder[i].reset_time_input, i, pixels, False
                )
            elif bug_holder[i].type == 3:
                bug_holder[i].reset_time_input = carolinus(
                    bug_holder[i].reset_time_input, i, pixels
                )
            # this is just a catchall if there is some sort of error
            else:
                bug_holder[i].reset_time_input = brimleyi(
                    bug_holder[i].reset_time_input, i, pixels
                )
            # print("number error")

        # briefly pauses the loop to avoid crashing the USB bus.
        #   Also makes it easier to see what is happening.
        time.sleep(0.1)
    print("twinkle done")
    pixels.fill((0, 0, 0))
    pixels.write()
    gc.collect()
