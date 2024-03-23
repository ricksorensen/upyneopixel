# from https://github.com/blaz-r/pi_pico_neopixel/blob/main/neopixel.py
def colorHSVfloat(hue, sat, val):
    return colorHSV(int(hue * 65535), int(sat * 255), int(val * 255))


def colorHSV(hue, sat, val):
    """
    Converts HSV color to rgb tuple and returns it.
    The logic is almost the same as in Adafruit NeoPixel library:
    https://github.com/adafruit/Adafruit_NeoPixel so all the credits for that
    go directly to them (license: https://github.com/adafruit/Adafruit_NeoPixel/blob/master/COPYING)

    :param hue: Hue component. Should be on interval 0..65535
    :param sat: Saturation component. Should be on interval 0..255
    :param val: Value component. Should be on interval 0..255
    :return: (r, g, b) tuple
    """
    if hue >= 65536:
        hue %= 65536

    hue = (hue * 1530 + 32768) // 65536
    if hue < 510:
        b = 0
        if hue < 255:
            r = 255
            g = hue
        else:
            r = 510 - hue
            g = 255
    elif hue < 1020:
        r = 0
        if hue < 765:
            g = 255
            b = hue - 510
        else:
            g = 1020 - hue
            b = 255
    elif hue < 1530:
        g = 0
        if hue < 1275:
            r = hue - 1020
            b = 255
        else:
            r = 255
            b = 1530 - hue
    else:
        r = 255
        g = 0
        b = 0

    v1 = 1 + val
    s1 = 1 + sat
    s2 = 255 - sat

    r = ((((r * s1) >> 8) + s2) * v1) >> 8
    g = ((((g * s1) >> 8) + s2) * v1) >> 8
    b = ((((b * s1) >> 8) + s2) * v1) >> 8

    return (r, g, b)


# simple conversion of 255 hues to rgb
def colorwheel(pos, bright=1):
    rv = [0, 0, 0]
    if 0 <= pos < 85:
        rv = [255 - pos * 3, pos * 3, 0]
    elif pos < 170:
        pos -= 85
        rv = [0, 255 - pos * 3, pos * 3]
    elif pos < 256:
        pos -= 170
        rv = [pos * 3, 0, 255 - pos * 3]
    for i in range(3):
        rv[i] = round(bright * (rv[i]))
    return rv


def testLed(pixel, scale=None, pause=2):
    import time

    for p in range(256):
        c = list(colorwheel(p))
        if scale is not None:
            for i in range(3):
                c[i] = c[i] // scale
        pixel[0] = c
        pixel.write()
        print("p: ", p, c)
        time.sleep(pause)
