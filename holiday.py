import time
import random
import gc
import runleds
import twinkle
import cbytes


# time.localtime()/gmtime() are UTC
# machine.RTC().datetime(): yr,mon,day,dow,hr,min,sec,microsec
# time.localtime(): yr,mon,day,hr,min,sec,dow, doy
# [3] is hour of day, UTC assumed
# 22h is 16h CST (no UTC) 17h CDT
# 23h is 17h CST          18h CDT
def rjslocaltime(tzoff=-6):
    return time.localtime(time.time() + (tzoff * 3600))


class Holiday:
    def __init__(self, pix, *, date=None, dur=100, nrandom=None, bright=0.1):
        self.pix = pix
        self.dur = dur
        self.nrandom = nrandom
        self.isHoliday = False
        self.bright = bright
        if date is not None:
            self.chkdate(dt=date)

    def setHoliday(self, isHoliday):
        self.isHoliday = isHoliday

    def chkDate(self, dt=None, run=False):
        return False

    def run(self):
        pass


class Hanukkah(Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1):
        self.data = runleds.test_data(expscale=6, b=0.25, pixlen=len(pix))
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)
        self.twinkdata = twinkle.hanukkah_col

    def chkDate(self, dt=None, run=False):
        if dt is None:
            dt = rjslocaltime()
        self.isHoliday = (dt[0] == 2024) and (dt[1] == 12) and (7 <= dt[2] <= 15)
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, choice=None):
        if choice is None:
            choice = random.choice([True, False])
        if choice:
            print("hanukkah full")
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=self.nrandom,
                bright=self.bright,
            )
        else:
            print("hanukkah twinkle")
            twinkle.doTwinkle(self.pix, self.twinkdata, tdur_sec=self.dur)
        gc.collect()


class Christmas(Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None):
        self.data = cbytes.hls_g_r_b_med if len(pix) > 75 else cbytes.hsv_g_r_b
        if sf is not None:
            self.data = runleds.scale_bytearray(self.data, sf)
        else:
            self.data = cbytes.hls_g_r_b_med
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkDate(self, dt=None, run=False):
        if dt is None:
            dt = rjslocaltime()
        self.isHoliday = dt[1] == 12
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, sf=None, choice=None):
        if choice is None:
            choice = random.choice([True, False])
        if choice:
            print("dochristmas")
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=self.nrandom,
                bright=self.bright,
            )
        else:
            print("twinkle")
            twinkle.doTwinkle(self.pix, tdur_sec=self.dur)
        gc.collect()


class Valentine(Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None, swaprg=True):
        self.data = runleds.test_data(
            ci=0, expscale=6, swaprg=swaprg, b=0.25, pixlen=len(pix)
        )
        self.twinkdata = twinkle.valentine_col
        if not swaprg:
            self.twinkdata = twinkle.swapGRB(self.twinkdata)
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkDate(self, dt=None, run=False):
        if dt is None:
            dt = rjslocaltime()
        self.isHoliday = (dt[1] == 2) and (14 == dt[2])
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, sf=None, choice=None):
        if choice is None:
            choice = random.choice([True, False])
        if choice:
            print("valentine")
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=self.nrandom,
                bright=self.bright,
            )
        else:
            print("twinkle")
            twinkle.doTwinkle(self.pix, self.twinkdata, tdur_sec=self.dur)
        gc.collect()


class SaintPatrick(Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None, swaprg=True):
        self.data = runleds.test_data(
            ci=1, expscale=6, swaprg=swaprg, b=0.25, pixlen=len(pix)
        )
        self.twinkdata = twinkle.stpat_col
        if not swaprg:
            self.twinkdata = twinkle.swapGRB(self.twinkdata)
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkDate(self, dt=None, run=False):
        if dt is None:
            dt = rjslocaltime()
        self.isHoliday = (dt[1] == 3) and (17 == dt[2])
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, sf=None, choice=None):
        if choice is None:
            choice = random.choice([True, False])
        if choice:
            print("st pattys")
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=self.nrandom,
                bright=self.bright,
            )
        else:
            print("twinkle")
            twinkle.doTwinkle(self.pix, self.twinkdata, tdur_sec=self.dur)
        gc.collect()


class Birthday(Holiday):
    bdays = [
        (4, 11),  # Lucas
        (4, 24),  # Jo
        (5, 2),  # Rozzi
        (5, 3),  # Bess
        (6, 4),  # Marnee
        (6, 7),  # Dane
        (6, 24),  # Andrea
        (8, 7),  # Soren
        (8, 16),  # Olie
        (8, 29),  # Max
        (9, 26),  # Mendel
        (12, 18),  # Rick
    ]

    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None):
        self.data = None
        if nrandom is None:
            nrandom = len(pix) // 3
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkBday(dt):
        rv = False
        for d in Birthday.bdays:
            if d == dt[1:3]:  # dt is tuple, not list
                return True
        return rv

    def chkDate(self, dt=None, run=False):
        if dt is None:
            dt = rjslocaltime()

        self.isHoliday = Birthday.chkBday(dt)
        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, sf=None, choice=None):
        print("birthday")
        runleds.loop_led_time(
            self.pix,
            self.data,
            tdur_secs=self.dur,
            sclr=True,
            nrandom=self.nrandom,
            bright=self.bright,
        )
