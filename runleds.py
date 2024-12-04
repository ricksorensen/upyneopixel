import time
import machine
import neopixel
import gc
import random
import colorsupport


def offall(pix=None):
    if pix is not None:
        pix.fill((0, 0, 0))
        pix.write()


def dofade_exp(ci=2, nstep=10, b=1, expscale=3):
    import math

    sf = 255 / math.exp(nstep / expscale)
    cu = []
    clevel = int(255 * b)

    for s in range(nstep):
        npv = int(b * sf * math.exp(s / expscale))
        cu.append([clevel if i == ci else npv for i in range(3)])
    print(cu)
    return cu


# @micropython.native
def fillpixel(src, leds, start=0, clear=True):
    if clear:
        leds.fill((0, 0, 0))
    if len(src) + start < len(leds):
        for i in range(len(src)):
            leds[i + start] = src[i]
    else:
        for i in range(len(src)):
            leds[(start + i) % len(leds)] = src[i]
    leds.write()


def barrayToPix(src, swaprgb=False):
    d = None
    if src is not None:
        d = []
        np = len(src) // 3
        for i in range(np):
            if not swaprgb:
                d.append((src[i * 3], src[i * 3 + 1], src[i * 3 + 2]))
            else:
                d.append((src[i * 3 + 1], src[i * 3], src[i * 3 + 2]))
    return d


def randomColor(bright):
    ci = random.randint(0, 255)
    return colorsupport.colorwheel(ci, bright=bright)


def dorandom(leds, nrandom=None, bright=1):
    if nrandom is not None and random.randint(0, 10) > 8:
        for _ in range(nrandom):
            rled = random.randint(0, len(leds) - 1)
            leds[rled] = randomColor(bright=bright)
        leds.write()
        gc.collect()


def loop_led_time(
    leds, src, tdur_secs=60, step=1, dly=0.1, sclr=False, nrandom=None, bright=0.1
):
    tend = tdur_secs
    if tdur_secs is not None:
        tend = time.ticks_add(time.ticks_ms(), tend * 1000)
    i = 0
    llen = len(leds)
    print("loop_led_time: npix = ", llen)
    while tend is None or time.ticks_ms() < tend:
        if src is not None:
            # if isinstance(src, bytearray):
            #    blitbuf(src, leds, i, clear=sclr, debug=False)
            # else:
            # fillpixel(pixarray, leds, start=i, clear=sclr)
            fillpixel(src, leds, start=i, clear=sclr)
        elif sclr:
            leds.fill((0, 0, 0))
        dorandom(leds, nrandom=nrandom, bright=bright)
        if dly:
            time.sleep(dly)
        i = (i + step) % llen
        if i == 0 and tend is None:
            gc.collect()
    offall(leds)
    gc.collect()


def test_setup(npix=300, pin=2, swaprgb=False):
    pix = neopixel.NeoPixel(machine.Pin(pin), npix, timing=1)
    if swaprgb:
        pix.ORDER = (0, 1, 2, 3)  # neopixel.NeoPixel.ORDER default is  (1, 0, 2, 3)
    pix.fill((0, 0, 0))
    pix.write()
    print("Test_setup: ", npix)
    return pix


# note that default color buffer order for micropython-lib
#   neopixel is G R B (not R G B)
def test_dataa(expscale=3, b=0.25, pixlen=300, reverse=True, ci=2):
    norm = 2 if reverse else 1
    step = min(pixlen // norm - 5, 50 // norm)
    fwd = dofade_exp(ci=ci, nstep=step, b=b, expscale=expscale)
    print(f"May need to fix: step={step} pixlen={pixlen} fwdlen={len(fwd)}")
    if reverse:
        fwd = fwd + fwd[::-1]
    return fwd


def scale_pixels(pdata, sf=0.5):
    x = []
    for p in pdata:
        x.append([min(int(z * sf + 0.5), 0xFF) for z in p])
    return x
