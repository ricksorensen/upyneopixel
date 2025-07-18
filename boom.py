# https://www.anirama.com/1000leds/1d-fireworks/
import random
import colorsupport
import time
import gc

NUM_SPARK = 8

sparkpos = NUM_SPARK * [0]  # led position
sparkvel = NUM_SPARK * [0]  # led/s
sparkcol = NUM_SPARK * [0]  # led fade from 1(255)
gravity = -0.004  # led/s/s


def HeatColor(temp, b=1):
    stemp = int(temp) * 191 // 256
    hramp = stemp & 0x3F
    c = None
    if stemp & 0x80:
        c = [255, 255, hramp]
    elif stemp & 0x40:
        c = [255, hramp, 0]
    else:
        c = [hramp, 0, 0]
    return c


def flare(pix, flarepos=0, vel=None, b=1):
    flareVel = vel
    if vel is None:
        flareVel = random.randint(50, 90) / 100  # led/iteration
    for i in range(5):
        sparkpos[i] = 0
        sparkvel[i] = random.randrange(256) / 255 * (flareVel / 5)
        sparkcol[i] = max(min(255, sparkvel[i] * 1000), 0)
    nflare = 0
    while flareVel >= -0.2:
        nflare += 1
        pix.fill((0, 0, 0))
        for i in range(5):
            sparkpos[i] = max(min(len(pix) - 1, sparkpos[i] + sparkvel[i]), 0)
            sparkvel[i] += gravity
            sparkcol[i] = max(min(255, sparkcol[i] - 0.8), 0)
            pix[int(sparkpos[i])] = HeatColor(sparkcol[i])  # % 50
        pix[int(flarepos)] = colorsupport.colorHSVfloat(0, 0, b)
        pix.write()
        # sleep(0.005)
        flarepos = max(min(len(pix) - 1, flarepos + flareVel), 0)
        flareVel += gravity  # slow down to peak, will go negative to descend
        b *= 0.98  # and fade
    gc.collect()
    return flarepos


def explodeloop(pix, flarepos=0):
    nsparks = min(int(flarepos / 2), NUM_SPARK)
    for i in range(nsparks):
        sparkpos[i] = flarepos
        sparkvel[i] = (random.randrange(0, 20000) / 10000) - 1
        sparkcol[i] = max(min(255, abs(sparkvel[i]) * 500), 0)
        sparkvel[i] = sparkvel[i] * flarepos / len(pix)
    sparkcol[0] = 255
    dgravity = gravity
    c1 = 120
    c2 = 50
    nboom = 0
    while sparkcol[0] > c2 / 128:
        # sleep(0.001)
        pix.fill((0, 0, 0))
        for i in range(nsparks):
            sparkpos[i] = max(min(len(pix) - 1, sparkpos[i] + sparkvel[i]), 0)
            sparkvel[i] += dgravity
            sparkcol[i] = max(min(255, sparkcol[i] * 0.99), 0)
            spidx = int(sparkpos[i])
            if sparkcol[i] > c1:
                pix[spidx] = [255, 255, int(255 * (sparkcol[i] - c1) / (255 - c1))]
            elif sparkcol[i] < c2:
                pix[spidx] = [int(255 * sparkcol[i] / c2), 0, 0]
            else:
                pix[spidx] = [255, int(255 * (sparkcol[i] - c2) / (c1 - c2)), 0]
        dgravity = dgravity * 0.99
        pix.write()
        nboom = nboom + 1
    time.sleep(0.005)
    pix.fill((0, 0, 0))
    pix.write()
    gc.collect()


def doall(pix, durms=50000, brightness=0.5, dly=5, vel=None):
    tstart = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), tstart) < durms:
        fp = flare(pix, vel=vel, b=brightness)
        print(f"#Flare Done position {fp}")
        time.sleep(0.5)
        explodeloop(pix, flarepos=fp)
        pix.fill((0, 0, 0))
        pix.write()
        time.sleep(dly)
