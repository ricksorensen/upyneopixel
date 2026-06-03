import effects
import logging
import random
import time
import gc
import config
from checkstart import getlightlevel

logger = logging.getLogger(__name__)


class Lightning(effects.effect):
    def __init__(self, pix, flashlen=16, brightness=255, debug=False):
        super().__init__(pix, debug=debug)
        self.brightness = brightness
        self.flashlen = flashlen

    def update(self):

        if random.random() < 0.01:
            flash_len = random.randint(3, self.flashlen)
            start = random.randint(0, self.npix - flash_len)

            for i in range(flash_len):
                self._pix[start + i] = (255, 255, 255)

            self._pix.write()
            time.sleep(0.1)

        for i in range(self.npix):
            r, g, b = self._pix[i]
            self._pix[i] = (int(r * 0.7), int(g * 0.7), int(b * 0.7))

        self._pix.write()


def run_flashes(pix, dur, flashlen=16):
    rv = False
    llevel = getlightlevel(report=False)
    print(f"run_flash  llevel={llevel}  len={flashlen} .. dur={dur}")
    if llevel > config._LDR_LIGHTNING:
        lf = Lightning(pix, flashlen=flashlen)
        tstart = time.ticks_ms()
        tdur = dur * 1000
        print("starting lightning")
        logger.warning(f"starting lightning- {llevel}")
        while time.ticks_diff(time.ticks_ms(), tstart) < tdur:
            lf.update()
            time.sleep(0.05)
        pix.fill((0, 0, 0))
        pix.write()
        rv = True
    else:
        print(f"not starting lightning level={llevel}")
        logger.warning(f"not starting lightning {llevel}")
    gc.collect()
    return rv


def testlight(pin=1, len=300, flashlen=16):
    import machine
    import neopixel

    p = neopixel.NeoPixel(machine.Pin(pin), len)
    lf = Lightning(p, flashlen=flashlen)

    while True:
        lf.update()
