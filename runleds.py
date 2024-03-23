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


def dofade_white(ci=2, nstep=10):
    cu = []
    for i in range(nstep):
        sf = (i * 255) // nstep
        cu.append([255 if i == ci else sf for i in range(3)])
    return cu


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


def fillpixel(leds, src, start=0):
    if len(src) + start < len(leds):
        for i in range(len(src)):
            leds[i + start] = src[i]
    else:
        for i in range(len(leds) - start):
            leds[start + i] = src[i]
        for i in range(len(src) - (len(leds) - start)):
            leds[i] = src[len(src) - (len(leds) - start) + i]


# @micropython.native
# note that default color buffer order for micropython-lib
#   neopixel is G R B (not R G B)
#
def blitbuf(src, leds, pixpos, clear=True, debug=False):
    if clear:
        leds.fill((0, 0, 0))
    llen = len(leds)  # pixels
    pixposu = pixpos % llen
    slen = len(src)  # buff bytes
    srcpixlen = slen // 3  # src len in pixels
    sp = 3 * pixposu  # sp in ledbuf in byte
    ep = min(sp + slen, llen * 3)  # end in ledbug in bytes, first write
    fwlen = ep - sp  # first write len in bytes
    if debug:
        print(f"srclen={slen} srcpixlen={srcpixlen} sp={sp} ep={ep} fwlen={fwlen}")
    if srcpixlen < llen:  # pattern should fit
        leds.buf[sp:ep] = src[:fwlen]
        if fwlen < slen:
            leds.buf[: slen - fwlen] = src[fwlen:]
        leds.write()


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
            blitbuf(src, leds, i, clear=sclr, debug=False)
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


def test_setup(npix=300, pin=2):
    pix = neopixel.NeoPixel(machine.Pin(pin), npix)
    pix.fill((0, 0, 0))
    pix.write()
    print("Test_setup: ", npix)
    return pix


# note that default color buffer order for micropython-lib
#   neopixel is G R B (not R G B)
def test_data(expscale=3, b=0.25, swaprg=True, pixlen=300, reverse=True, ci=2):
    norm = 2 if reverse else 1
    step = min(pixlen // norm - 5, 50 // norm)
    fwd = dofade_exp(ci=ci, nstep=step, b=b, expscale=expscale)
    print(f"May need to fix: step={step} pixlen={pixlen} fwdlen={len(fwd)}")
    alld = []
    for x in fwd:
        if swaprg:
            alld.extend([x[1], x[0], x[2]])
        else:
            alld.extend(x)
    if reverse:
        bkwd = fwd.copy()
        bkwd.reverse()

        for x in bkwd:
            if swaprg:
                alld.extend([x[1], x[0], x[2]])
            else:
                alld.extend(x)
    return bytearray(alld)


def scale_bytearray(bary, sf=0.5):
    x = bytearray(len(bary))
    for i in range(len(bary)):
        x[i] = min(int(sf * bary[i] + 0.5), 0xFF)
    return x


def scale_bytearray_inplace(bary, sf=0.5):
    for i in range(len(bary)):
        bary[i] = min(int(sf * bary[i] + 0.5), 0xFF)
    return bary  # to match above


# @micropython.native
def shift_buf(pix, n):
    lb = len(pix.buf)
    nbys = n * 3
    tbuf = bytearray(nbys)
    tbuf = pix.buf[lb - nbys :]
    pix.buf[nbys:] = pix.buf[: lb - nbys]
    pix.buf[:nbys] = tbuf
    gc.collect()
