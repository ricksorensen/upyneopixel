import holiday
import randBlinkerFade as doeyes
import random
import gc

__ONTIME_CDT = 18  # hour CDT to start
__neyes = 8
__mrate = 25


def set_eyecolor(cfwd, cbkw):
    doeyes.cfwd = cfwd
    doeyes.cbkw = cbkw


def selecteyes(
    pix,
    neyes,
    moverate,
    ncycles=3,
    blink=True,
    ctlim=20000,
    faderate=1,
    fadeamt=3,
    flyctlim=5000,
    flyrate=0.5,
    flybounce=True,
    flyblink=False,
):
    doeyes.offall(pix)
    while ncycles > 0:
        print("cycle: ", ncycles)
        if random.randrange(10) > 3:
            print("many eyes")
            doeyes.movesome(
                pix,
                len(pix),
                neyes=neyes,
                moverate=moverate,
                blink=True,
                ctlim=ctlim,
                faderate=faderate,
                fadeamt=fadeamt,
            )
        else:
            print("flying eyes")
            doeyes.fly(
                pix,
                len(pix),
                moverate=flyrate,
                reverse=flybounce,
                ctlim=flyctlim,
                blink=flyblink,
                deltaeye=6,
            )
        ncycles = ncycles - 1


class Halloween(holiday.Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1):
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkDate(self, dt=None, run=False, bright=None):
        if dt is None:
            dt = holiday.rjslocaltime()
        self.isHoliday = (dt[1] == 10) and (dt[2] >= 25)
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, choice=None, bright=None):
        if bright is None:
            bright = self.bright
        neyeu = len(self.pix) // 15
        selecteyes(
            self.pix,
            neyes=neyeu,  # __neyes,
            moverate=__mrate,
            ncycles=15,
            blink=True,
            ctlim=1500,  # 1500 steps at 0.2s/step is 300s/5m
            faderate=1,
            fadeamt=3,
            flyctlim=2400,  # 2400 steps at .1/2 step is 120s/3m
            flyrate=0.1,
            flybounce=True,
            flyblink=False,
        )
        gc.collect()
