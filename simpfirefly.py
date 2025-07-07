import gc
import random
import time

colors = [
    (232, 100, 255),  # Purple
    (200, 200, 20),  # Yellow
    (30, 200, 200),  # Blue
    (150, 50, 10),
    (50, 200, 10),
]


max_len = 500
min_len = 50
# pixelnum, posn in flash, flash_len, direction


def run_flies(pix, num_flashes=10, dur=120, bright=1.0):
    npix = len(pix)
    cu = [(int(c[0] * bright), int(c[1] * bright), int(c[2] * bright)) for c in colors]
    flashing = []
    for i in range(num_flashes):
        ipix = random.randint(0, npix - 1)
        col = random.randint(1, len(colors) - 1)
        flash_len = random.randint(min_len, max_len)
        flashing.append([ipix, cu[col], flash_len, 0, 1])
    pix.fill((0, 0, 0))
    tstart = time.ticks_ms()
    tdur = dur * 1000
    while time.ticks_diff(time.ticks_ms(), tstart) < tdur:
        for i in range(num_flashes):
            ipix = flashing[i][0]
            brightness = flashing[i][3] / flashing[i][2]
            colr = (
                int(flashing[i][1][0] * brightness),
                int(flashing[i][1][1] * brightness),
                int(flashing[i][1][2] * brightness),
            )
            try:
                pix[ipix] = colr
            except Exception:
                print(f"OOPS: {pix} idx={ipix} col={colr}")

            if flashing[i][2] == flashing[i][3]:
                flashing[i][4] = -1
            if flashing[i][3] == 0 and flashing[i][4] == -1:
                ipix = random.randint(0, npix - 1)
                col = random.randint(0, len(colors) - 1)
                flash_len = random.randint(min_len, max_len)
                flashing[i] = [ipix, colors[col], flash_len, 0, 1]
            flashing[i][3] = flashing[i][3] + flashing[i][4]
        pix.write()
        time.sleep(0.05)
    pix.fill((0, 0, 0))
    pix.write()
    gc.collect()


def testit(pin=2, plen=120, num_flashes=20, dur=10000, bright=1.0):
    import neopixel
    import machine

    run_flies(
        neopixel.NeoPixel(machine.Pin(pin), plen),
        num_flashes=num_flashes,
        dur=dur,
        bright=bright,
    )
