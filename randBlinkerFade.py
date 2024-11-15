import time
import random

# import neopixel
# import machine

# LED_PIN = 26   # PICO pin 1
# LED_PIN = 2  # XIAO ESP32C3 pin 1
# num_leds = 120
# pixels = neopixel.NeoPixel(machine.Pin(LED_PIN), num_leds)


class Blinker:
    def __init__(self, pos, led, color=[127, 40, 0], autoblink=False):
        self.active = False
        # self.deadtime=deadtime
        self.pos = pos % len(led)
        self.num_leds = len(led)
        self.color = color
        # self.speed=speed
        # self.intensity=intensity
        self.led = led
        # self.state = 0 # off
        # self.lastupdt = time.ticks_ms()
        self.opentime = None
        self.closetime = None
        self.autoblink = autoblink
        self.closetrange = [10000, 14000]
        self.opentrange = [1000, 2000]

    def __repr__(self):
        rv = "Blinker: active={} pos={} color={} opent={} closet={}".format(
            self.active, self.pos, self.color, self.opentime, self.closetime
        )
        return rv

    def setposx(self, pos):
        cu = self.led[self.pos]
        pos = pos % self.num_leds
        e2pos = (pos + 1) % self.num_leds
        self.led[self.pos] = (0, 0, 0)
        self.led[(self.pos + 1) % self.num_leds] = (0, 0, 0)
        self.pos = pos
        if self.active:
            self.led[pos] = cu
            self.led[e2pos] = cu
        else:
            self.led[pos] = (0, 0, 0)
            self.led[e2pos] = (0, 0, 0)
        self.led.write()

    def setpos(self, pos):
        cu = self.led[self.pos]
        pos = pos % self.num_leds
        self.led[self.pos] = (0, 0, 0)
        self.led[self.pos + 1] = (0, 0, 0)
        self.pos = pos
        if self.active:
            self.led[pos] = cu
            self.led[pos + 1] = cu
        else:
            self.led[pos] = (0, 0, 0)
            self.led[pos + 1] = (0, 0, 0)
        self.led.write()

    def setcolor(self, color):
        self.color = color
        self.led.write()

    def setautoblink(self, doblink):
        self.autoblink = doblink
        self.start()

    def isactive(self):
        return self.active

    def start(self, now=None):
        if now is None:
            now = time.ticks_ms()
        self.opentime = now
        self.check(now)

    def check(self, now, fade=None):
        if self.autoblink:
            # td = time.ticks_diff(now, self.lastupdt)
            if self.active and now >= self.closetime:
                # print("closing {}".format(self.pos))
                self.active = False
                cu = [0, 0, 0]
                if fade is not None:
                    cu = [max(c - fade, 0) for c in self.led[self.pos]]
                    if max(cu) > 0:
                        # print("fading .. ", self.pos, "  ", cu)
                        self.active = True
                    else:
                        self.opentime = time.ticks_add(
                            now, random.randint(*self.opentrange)
                        )
                        # print("fading done", self.pos)
                self.led[self.pos] = cu
                self.led[self.pos + 1] = cu
                self.led.write()
            elif (
                (not self.active)
                and (self.opentime is not None)
                and (now >= self.opentime)
            ):
                self.led[self.pos] = self.color
                self.led[self.pos + 1] = self.color
                self.closetime = time.ticks_add(now, random.randint(*self.closetrange))
                self.active = True
                self.led.write()
        else:
            if not self.active:
                self.led[self.pos] = self.color
                self.led[self.pos + 1] = self.color
                self.active = True
                self.led.write()


def offall(pixels):
    pixels.fill((0, 0, 0))
    pixels.write()


cltr = [1000, 2000]
optr = [2000, 3000]

crun = [64, 20, 0]


# c = [127,40,0] for RGB
# c = [40,127,0] for GRB
def runall(pix, npix, faderate=None, fadeamt=1, ctlim=2000):
    num_leds = len(pix)
    offall(pix)
    npix = min(npix, num_leds)
    ct = 0
    eyes = [Blinker(i, pix, color=crun, autoblink=True) for i in range(0, npix, 2)]
    now = time.ticks_ms()
    for b in eyes:
        b.opentrange = optr
        b.closetrange = cltr
        if random.choice([True, False]):
            b.start(now)
        else:
            b.opentime = time.ticks_add(now, random.randint(*b.opentrange))

    while ct < ctlim:
        fade = None
        if faderate is not None and (ct % faderate == 0):
            fade = fadeamt
        for b in eyes:
            b.check(time.ticks_ms(), fade=fade)
        time.sleep(0.2)
        ct = ct + 1
    return eyes


cfwd = [63, 20, 0]  # [20, 63, 0]
cbkw = [30, 6, 0]  # [6, 30, 0]  # [15, 0, 10] [12, 10, 0] [10,35,0],[12,10,0]


def movetwo(pix, npix=20, moverate=10):
    num_leds = len(pix)
    offall(pix)
    npix = min(npix, num_leds)
    ct = 0
    eyes = [
        Blinker(0, pix, autoblink=False),
        Blinker(npix - 2, pix, autoblink=False),
    ]

    now = time.ticks_ms()
    eyes[0].start(now)
    eyes[1].start(now)
    movet = time.ticks_add(now, moverate * 1000)
    while ct < 600:
        now = time.ticks_ms()
        if time.ticks_diff(now, movet) >= 0:
            eyes[0].setpos((eyes[0].pos + 2) % npix)
            eyes[1].setpos((eyes[1].pos - 2) % npix)
            movet = time.ticks_add(now, moverate * 1000)
        #        for b in eyes:
        #            b.check(n)
        time.sleep(0.1)
        ct = ct + 1
    return eyes


def fly(pix, npix, moverate=10, reverse=False, ctlim=2000, blink=False, deltaeye=2):
    num_leds = len(pix)
    offall(pix)
    npix = min(npix, num_leds)
    ct = 0
    eye = Blinker(0, pix, color=cfwd, autoblink=blink)
    now = time.ticks_ms()
    eye.start(now)
    delta = deltaeye
    moveratems = int(moverate * 1000)
    movet = time.ticks_add(now, moveratems)
    sleeptime = moverate / 2.0
    while (ctlim is None) or (ct < ctlim):
        now = time.ticks_ms()
        if time.ticks_diff(now, movet) >= 0:
            newpos = (eye.pos + delta) % npix
            if reverse:
                if delta > 0 and (newpos == 0 or (newpos == npix - 1)):
                    newpos = npix - 4
                    delta = -deltaeye
                elif delta < 0 and newpos >= npix - 2:
                    newpos = 2
                    delta = deltaeye
            else:
                if newpos > npix - 2:
                    newpos = 0

            eye.setpos(newpos)
            eye.check(now)
            movet = time.ticks_add(now, moveratems)
        time.sleep(sleeptime)
        ct = ct + 1
    return eye


def movesome(
    pix,
    npix,
    neyes=2,
    moverate=10,
    blink=False,
    ctlim=600,
    faderate=None,
    fadeamt=2,
):
    num_leds = len(pix)
    offall(pix)
    npix = min(npix, num_leds)
    ct = 0
    eyes = []
    for i in range(neyes):
        cu = cfwd if i % 2 == 0 else cbkw
        eyes.append(
            Blinker(
                2 * random.randint(0, (npix // 2) - 1),
                pix,
                color=cu,
                autoblink=blink,
            )
        )
    print("Num Eyes: ", len(eyes))
    print(eyes)
    now = time.ticks_ms()
    for eye in eyes:
        eye.start(now)
    movet = time.ticks_add(now, moverate * 1000)
    while ctlim is None or ct < ctlim:
        now = time.ticks_ms()
        n = time.ticks_diff(now, movet)
        if n >= 0:
            for i in range(len(eyes)):
                eye = eyes[i]
                if random.randint(0, 100) < 5:
                    np = 2 * random.randint(0, (npix // 2) - 1)
                    # eye.setcolor(
                    #    (eye.color[0], eye.color[1], (eye.color[2] + 10) % 256)
                    # )
                elif i % 2 == 0:
                    np = (eye.pos + 2) % npix
                else:
                    np = (eye.pos - 2) % npix
                eye.setpos(np)
            movet = time.ticks_add(now, moverate * 1000)
        if blink:
            fade = None
            if faderate is not None and (ct % faderate == 0):
                fade = fadeamt
            for b in eyes:
                b.check(n, fade=fade)
        time.sleep(0.2)
        ct = ct + 1
    return eyes
