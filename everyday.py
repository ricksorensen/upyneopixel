from holiday import Holiday
import runleds
import colorsupport


def mapRange(value, inMin, inMax, outMin, outMax):
    return outMin + (((value - inMin) / (inMax - inMin)) * (outMax - outMin))


# fade saturation for hsv0 from 1 to 0, fixed brightness (value)
def fadeHue(h, nstep=10, b=0.25, swaprg=True, reverse=True):
    fwd = []
    for i in range(nstep):
        np = colorsupport.colorHSVfloat(h / 360, (1 - i / nstep), b)
        fwd.append(np)
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


class Everyday(Holiday):
    def __init__(self, pix, *, dur=100, nrandom=None, bright=0.1, sf=None):
        self.data = None
        self.tmin = -5
        self.tmax = 35
        # if nrandom is None:
        #    nrandom = len(pix) // 3
        super().__init__(pix, dur=dur, nrandom=nrandom, bright=bright)

    def run(self, *, sf=None, choice=None, correct=0, swaprg=True):
        import esp32

        t = min(max(esp32.mcu_temperature() - correct, self.tmin), self.tmax)
        # h = (168 - 4.8 * t)/360*65536
        temphue = mapRange(t, self.tmin, self.tmax, 220, 0)
        self.data = fadeHue(temphue, nstep=(len(self.pix) // 2 - 10), swaprg=swaprg)
        print("everyday {}+{}".format(t, correct))
        runleds.loop_led_time(
            self.pix,
            self.data,
            tdur_secs=self.dur,
            sclr=True,
            nrandom=self.nrandom,
            bright=self.bright,
        )
        return t
