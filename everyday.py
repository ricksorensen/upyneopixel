from holiday import Holiday, rjslocaltime
import runleds
import colorsupport
import onewire
import ds18x20
import config
import machine

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
        self.data = None
        self.tmin = -15
        self.tmax = 35
        self.tempsens = None
        self.fixtemp = fixtemp
        try:
            temppin = config._TEMP_PIN
            tsens = ds18x20.DS18X20(onewire.OneWire(machine.Pin(temppin)))
            rs = tsens.scan()
            if len(rs) == 0:
                print("no tempsensor found")
                self.tempsens = None
            else:
                self.tempsens = (tsens, rs[0])
        except:
            self.tempsens = None
            print("exception while checking temp sensor")
        # if nrandom is None:
        #    nrandom = len(pix) // 3
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def run(self, *, sf=None, choice=None, correct=0):
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

        print("everyday t={}, texternal={}, tmcu={}+{}".format(t, tout, tmcu, correct))
        if (tod[4] % 15) < 5:
            runleds.loop_led_time(
                self.pix,
                self.data,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=nrand,
                bright=self.bright,
            )
        else:
            runleds.loop_led_time(
                self.pix,
                None,
                tdur_secs=self.dur,
                sclr=True,
                nrandom=len(self.pix) // 3,
                bright=self.bright,
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
        except:
            print("exception while checking temp sensor")
        return c, tout
