# import colorsupport
import gc
import random

try:
    from micropython import const
    from time import ticks_ms, ticks_diff, sleep

    stime = ticks_ms()
except (ModuleNotFoundError, AttributeError):
    from time import monotonic, sleep

    def const(x):
        return x

    def ticks_ms():
        return monotonic() * 1000

    def ticks_diff(t1, t0):
        return t1 - t0


NUM_SPARK = const(30)


class Particle:
    def __init__(self, pos, v, c, a=-9.8, dur=None):
        self.x = pos  # m
        self.v = v  # maxspeed*random(-1,1)  m/s
        self.a = a  # m/s/s
        self.c = c
        self.l = dur
        # self._px = pos
        self.lastupdate = self.birth = ticks_ms()

    def __repr__(self):
        return f"{self.age():.3f}, {self.x:.2f}, {self.v:.4f}, {self.a:.4f}, {self.c}"

    # age in seconds
    def age(self):
        return ticks_diff(ticks_ms(), self.birth) / 1000

    def alive(self):
        return self.l is None or self.l > 0

    def kill(self):
        self.l = 0

    # update by dt seconds
    def update(self, dt=None):
        if self.alive():
            # euler
            if dt is None:
                dt = ticks_diff(ticks_ms(), self.lastupdate) / 1000  # sec
            self.v += self.a * dt
            self.x += self.v * dt
            self.lastupdate = ticks_ms()
            # self.c = fade
            if self.l:
                self.l = self.l - dt


def flare(
    pix,  # neopixel
    *,
    vlim=-10,  # stop when falling is faster than this
    v0=34.5,  # initial velocity
    a=-9.8,  # acceleration
    iterlim=1000,  # maximum number of steps
    sampinterval=0.02,  # time interval
    fcolor=0,  #
    useiter=False,  # use steps (iteration count) instead of time
    debugprint=False,
    norm=1,
):
    dt = 1 if useiter else None
    # max -v0/a per x=0 + v0*t + a*t*t/2
    p = Particle(0, v0, None, a=a)
    i = 0
    b = 1
    if debugprint:
        print(f"# vlim={vlim} v0={v0}  a0={a} flare()")
        print("#t,x,v,c")
    while (p.v > vlim) and (i < iterlim):
        pix.fill((0, 0, 0))
        # pix.fill((0,0,0))
        p.update(dt)
        if debugprint:
            print(p)
        # pix[int(p)]=colorsupport.colorHSVfloat(fcolor,0,b)  # sat 0 gives white
        fc = int(255 * b)  # if white just do a bit
        pix[int(p.x / norm)] = (fc, fc, fc)
        pix.write()
        sleep(sampinterval)
        i += 1
        b *= 0.99  # fade
    p.kill()
    if debugprint:
        print(f"#flare: num steps {i}")
    gc.collect()
    return p.x


def sparksalive(sparks):
    # return not all(not s.alive() for s in sparks)
    return any(s.alive() for s in sparks)


def explodeloop(
    pix,  # neopixel
    flarepos=0,  # starting position for boom
    a=-9.8,  # acceleration
    sampinterval=0.02,  # time interval
    useiter=False,  # use steps (iteration count) instead of time
    debugprint=False,
    norm=1,
):
    nsparks = min(int(flarepos / 2), NUM_SPARK)
    sparks = []
    for i in range(nsparks):
        sv = (random.randrange(0, 20000) / 10000) - 1  # factor for starting vel
        sparks.append(
            Particle(
                flarepos,
                sv * 15,  # flarepos / (len(pix) * norm),  # what should this be??
                255 if i == 0 else max(min(255, abs(sv) * 500), 0),  # color
                a=a,
                dur=2.5 + 1.5 * random.randrange(0, 100) / 100,
            )
        )
    if debugprint:
        for s in sparks:
            print(s)
    dgravity = a
    dt = 1 if useiter else None
    c1 = 120
    c2 = 50
    nboom = 0
    if debugprint:
        print(f"#nboom {nboom}. col {[sc.c for sc in sparks]}")
        print(
            "#t,p1,p2,p3,p4,p5,p6,p7,p8,v1,v2,v3,v4,v5,v6,v7,v8,c1,c2,c3,c4,c5,c6,c7,c8"
        )
    # ts = ticks_ms()
    while sparksalive(sparks):
        # sleep(0.001)
        pix.fill((0, 0, 0))
        for i in range(nsparks):
            sparks[i].update(dt)
            spc = sparks[i].c = max(min(255, sparks[i].c * 0.99), 0)
            spidx = max(min(len(pix) - 1, int(sparks[i].x / norm)), 0)
            if spc > c1:
                pix[spidx] = [255, 255, int(255 * (spc - c1) / (255 - c1))]
            elif spc < c2:
                pix[spidx] = [int(255 * spc / c2), 0, 0]
            else:
                pix[spidx] = [255, int(255 * (spc - c2) / (c1 - c2)), 0]
        dgravity = dgravity * 0.99
        pix.write()
        sleep(sampinterval)
        nboom = nboom + 1
        if debugprint:
            print(
                f"{sparks[0].age():.4f},"
                + ",".join(map("{:.2f}".format, [sc.x for sc in sparks]))
                + ","
                + ",".join(map("{:.4f}".format, [sc.v for sc in sparks]))
                + ","
                + ",".join(map("{:.1f}".format, [sc.c for sc in sparks]))
            )
    if debugprint:
        print(f"#explode: num steps {nboom}")
    sleep(sampinterval)
    pix.fill((0, 0, 0))
    pix.write()


def testit(
    pix,
    vlim=-2,
    v0=73.33,
    a=-9.8,
    iterlim=1000,
    sampinterval=0.01,
    useiter=False,
    debugprint=False,
    norm=None,
):
    if norm is None:
        flare_max = -(v0 * v0) / a / 2
        norm = (flare_max * 1.15) / len(pix)
        print(f"flare_max={flare_max}   normu={norm}")
    print(f"fw.testit {norm} {v0}")
    flarepos = flare(
        pix,
        vlim=vlim,
        v0=v0,
        a=a,
        iterlim=iterlim,
        sampinterval=sampinterval,
        useiter=useiter,
        debugprint=debugprint,
        norm=norm,
    )
    gc.collect()
    explodeloop(
        pix,
        flarepos=flarepos,
        a=a,
        sampinterval=sampinterval,
        useiter=useiter,
        debugprint=debugprint,
        norm=norm,
    )
    gc.collect()


def doall(pix, durms=15000, dly=2, vel=73, norm=None, debugprint=False):
    tstart = ticks_ms()
    while ticks_diff(ticks_ms(), tstart) < durms:
        testit(pix, v0=vel, useiter=False, norm=norm, vlim=-1.0, debugprint=debugprint)
        sleep(dly)
