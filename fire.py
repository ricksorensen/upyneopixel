import holiday
import effect_panel
import gc
import time
import random


# duration in milliseconds
# update in milliseconds
class Fire(holiday.Holiday):
    def __init__(
        self,
        pix,
        *,
        dur=100,
        update=10,
        nrandom=None,
        top=True,
        bright=0.1,
        debug=False,
    ):
        self.debug = debug
        self.update = update
        self.dur = dur
        self.top = top
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def chkDate(self, dt=None, run=False, bright=None):
        if dt is None:
            dt = holiday.rjslocaltime()
        self.isHoliday = (dt[1] == 7) and (dt[2] <= 4)

        if self.isHoliday and run:
            self.run()
        return self.isHoliday

    def run(self, *, choice=None, bright=None):
        if bright is None:
            bright = self.bright
        firetop = random.choice([True, False]) if self.top is None else self.top
        print(f"fire {self.dur} {self.update} {firetop}")
        gc.collect()
        panel = effect_panel.effect_panel(
            self.pix, 36, 2 if len(self.pix) < 200 else 6, ledblock=5
        )
        nflgiter = 2 if len(self.pix) < 200 else 3
        tstart = time.ticks_ms()
        ct = 0
        while time.ticks_diff(time.ticks_ms(), tstart) < self.dur:
            panel.firelight(
                brightness=min(int(bright * 255), 255),
                red=255,
                green=64,
                blue=10,
                speed=128,
                fade=255,
                top=firetop,
                debug=self.debug,
            )
            if ct == 0:
                panel.flag(
                    top=not firetop,
                    niter=nflgiter,
                    brightness=min(int(bright * 255), 255),
                    debug=self.debug,
                )
            ct = (ct + 1) % 4
            panel.update()
            time.sleep_ms(self.update)
        gc.collect()
