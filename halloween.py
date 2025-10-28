import holiday
import randBlinkerFade as doeyes
import random
import gc
import logging
import config

logger = logging.getLogger(__name__)


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
    dur=300,
    gap=1,
    faderate=1,
    fadeamt=3,
    flydur=120,
    flyrate=0.5,
    flybounce=True,
    flyblink=False,
):
    doeyes.offall(pix)
    while ncycles > 0:
        logger.debug(f"cycle: {ncycles}")
        if random.randrange(10) > 3:
            logger.debug("many eyes")
            doeyes.movesome(
                pix,
                len(pix),
                neyes=neyes,
                moverate=moverate,
                blink=True,
                gap=gap,
                tdur_secs=dur,
                faderate=faderate,
                fadeamt=fadeamt,
            )
        else:
            logger.debug("flying eyes")
            doeyes.fly(
                pix,
                len(pix),
                gap=gap,
                moverate=flyrate,
                reverse=flybounce,
                tdur_secs=flydur,
                blink=flyblink,
                deltaeye=6,
            )
        ncycles = ncycles - 1


class Halloween(holiday.Holiday):
    def __init__(self, pix, *, dur=100, gap=1, neyes=None, nrandom=None, bright=0.1):
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)
        self.gap = gap
        self.neyes = neyes if neyes is not None else len(self.pix) // 15

    def chkDate(self, dt=None, run=False, bright=None):
        if dt is None:
            dt = holiday.rjslocaltime()
        self.isHoliday = (dt[1] == 10) and (dt[2] >= 15)
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, choice=None, bright=None):
        if bright is None:
            bright = self.bright
        logger.warning("starting halloween ~ 5min")
        selecteyes(
            self.pix,
            neyes=config._NEYES,  # self.neyes,  __neyes,
            moverate=__mrate,
            ncycles=5,
            blink=True,
            dur=self.dur,  # 1500 steps at 0.2s/step is 300s/5m
            gap=self.gap,
            faderate=1,
            fadeamt=3,
            flydur=self.dur,  # 2400 steps at .1/2 step is 120s/3m
            flyrate=config._FLYRATE,
            flybounce=True,
            flyblink=False,
        )
        gc.collect()
