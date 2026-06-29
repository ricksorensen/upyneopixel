from holiday import Holiday, rjslocaltime
import runleds
import colorsupport
import onewire
import ds18x20
import config
import machine
import random
import simpfirefly
import lightning

# import boom
import fwpartx

import logging

logger = logging.getLogger(__name__)


try:
    haveTemp = True
    import esp32

except ImportError:
    haveTemp = False


def get_temp(tmin, tmax, correct=0, tempsens=None):
    extt = None
    tmcu = min(max(esp32.mcu_temperature() - correct, tmin), tmax) if haveTemp else None
    if isinstance(tempsens, int):
        extt = tempsens
    elif tempsens is not None:
        import time

        tempsens[0].convert_temp()
        time.sleep_ms(750)
        extt = min(max(tempsens[0].read_temp(tempsens[1]), tmin), tmax)
    return (extt, tmcu)


def mapRange(value, inMin, inMax, outMin, outMax):
    return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))


def crossHue2a(h, nstep=10, b=0.25, reverse=True, swaprgb=False):
    fwd = []
    dh = 30 / nstep
    hi = h - 30
    for i in range(nstep):
        np = colorsupport.colorHSVfloat(
            (int(hi) % 360) / 360, 1, b, swaprgb=swaprgb, greenmute=0.3
        )
        fwd.append(np)
        hi = hi + 2 * dh
    if reverse:
        fwd = fwd.extend(fwd[::-1])
    # return bytearray(alld)
    return fwd


class Everyday(Holiday):
    def __init__(
        self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None, fixtemp=None
    ):
        self.ffnum = 0
        self.temp = False
        self.dorand = False
        try:
            if "FF" in config._EVERYDAY_OPT:
                self.ffnum = 20
                ifn = config._EVERYDAY_OPT.find("FFNUM=")
                if ifn >= 0:
                    ife = ifn + config._EVERYDAY_OPT[ifn:].find(",")
                    self.ffnum = int(config._EVERYDAY_OPT[ifn + 6 : ife])
            self.temp = "TEMP" in config._EVERYDAY_OPT
            self.dorand = "RAND" in config._EVERYDAY_OPT
        except AttributeError:
            self.ffnum = 0
        self.data = None
        self.tmin = -25
        self.tmax = 35
        self.tempsens = None
        self.fixtemp = fixtemp
        try:
            temppin = config._TEMP_PIN
            tsens = ds18x20.DS18X20(onewire.OneWire(machine.Pin(temppin)))
            rs = tsens.scan()
            if len(rs) == 0:
                logger.warning("no tempsensor found")
                self.tempsens = None
            else:
                self.tempsens = (tsens, rs[0])
        except Exception as excp:
            self.tempsens = None
            logger.exception("exception while checking temp sensor", exc_info=excp)
        # if nrandom is None:
        #    nrandom = len(pix) // 3
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def run(self, *, sf=None, choice=None, correct=0, bright=None):
        if bright is None:
            bright = self.bright
        tod = rjslocaltime()
        try:
            tout, tmcu = get_temp(
                self.tmin,
                self.tmax,
                correct,
                tempsens=self.tempsens if self.fixtemp is None else self.fixtemp,
            )
            t = tout if tout is not None else tmcu
            if t is None:
                t = 24
            # h = (168 - 4.8 * t)/360*65536
            temphue = mapRange(t, self.tmin, self.tmax, 220, -40)
            self.data = crossHue2a(
                temphue,
                nstep=(len(self.pix) // 2 - 10),
                reverse=False,
                swaprgb=config._SWAPRGB,
            )
            nrand = self.nrandom
        except ImportError:
            self.data = None
            t = None
            nrand = len(self.pix) // 3

        logger.debug("everyday t={},  nff={}".format(tout, self.ffnum))
        if self.temp and (("TEMP" in config._EVERYDAY_OPT) or ((tod[4] % 30) < 5)):
            logger.warning(f"starting everyday runtemp {self.dur}")
            # print("everyday runtemp")
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=nrand,
                bright=bright,
            )
            # simpfirefly.run_flies(self.pix, num_flashes=20, dur=self.dur, bright=bright)
        else:
            opt = random.randrange(0, 100)
            if "LIGHTNING" in config._EVERYDAY_OPT:
                # print("everyday lightning")
                logger.warning(f"asking to start everyday lightning {self.dur}")
                if lightning.run_flashes(self.pix, dur=self.dur):
                    return t
            if opt < 30 and self.ffnum > 0:
                # print("everyday firefly")
                logger.warning(f"starting everyday firefly  {self.dur}")
                simpfirefly.run_flies(
                    self.pix, num_flashes=self.ffnum, dur=self.dur, bright=bright
                )
            elif 30 <= opt < 80 and self.dorand:
                flowdir = random.choice((True, False))
                # print(f"everyday random flowdir = {flowdir}")
                logger.warning(f"starting everyday random {self.dur}")
                runleds.loop_led_time(
                    self.pix,
                    None,
                    dly=config._FLOW_DELAY,
                    tdur_secs=self.dur,
                    # sclr=True,
                    nrandom=len(self.pix) // 3,
                    bright=bright,
                    flow=True,
                    flowdir=flowdir,
                )
            elif opt >= 80 and "FWORK" in config._EVERYDAY_OPT:
                # print("everyday firework")
                logger.warning(f"starting everyday fireworks {self.dur}")
                # should be fireworks
                # boom.doall(self.pix, durms=self.dur * 1000, brightness=bright, dly=2)
                norm = None
                # if len(self.pix) < 200:
                #    norm = 2.4
                fwpartx.doall(self.pix, vel=80, durms=self.dur * 1000, dly=2, norm=norm)
            else:
                # print("everyday random no flow")
                logger.warning(f"starting everyday random no flow {self.dur}")
                runleds.loop_led_time(
                    self.pix,
                    None,
                    tdur_secs=self.dur,
                    sclr=True,
                    nrandom=len(self.pix) // 3,
                    bright=bright,
                    flow=False,
                )
        return t

    def getTempColor(self, b=0.2):
        c = (0, 0, 0)
        tout = None
        try:
            tout, tmcu = get_temp(
                self.tmin,
                self.tmax,
                correct=0,
                tempsens=self.tempsens if self.fixtemp is None else self.fixtemp,
            )
            # h = (168 - 4.8 * t)/360*65536
            if tout is not None:
                temphue = mapRange(tout, self.tmin, self.tmax, 220, -40)
                c = colorsupport.colorHSVfloat(
                    (int(temphue) % 360) / 360,
                    1,
                    b,
                    swaprgb=config._SWAPRGB,
                    greenmute=0.3,
                )
        except Exception as excp:
            logger.exception("exception while checking temp sensor", exc_info=excp)
        return c, tout


class Aprilfool(Everyday):
    def run(self, *, bright=None):
        logger.warning("April Fools")
        super().run(bright)

    def chkDate(self, dt=None, run=False, bright=None):
        if dt is None:
            dt = rjslocaltime()
        self.isHoliday = (dt[1] == 4) and (dt[2] == 1)
        if self.isHoliday and run:
            self.run(bright=bright)
        return self.isHoliday
