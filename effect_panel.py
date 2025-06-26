from time import sleep
from random import randint
import gc

pixreal = False
try:
    from neopixel import NeoPixel
    from time import sleep_ms

    pixreal = True
except ModuleNotFoundError:
    from upy_backend import NeoPixel

    pixreal = False


def makeRWB(n, b):
    mypix = []
    mc = b
    for _ in range(n):
        mypix.append((mc, 0, 0))
    for _ in range(n):
        mypix.append((mc, mc, mc))
    for _ in range(n):
        mypix.append((0, 0, mc))
    return mypix


def _makeflag(pix, size=30, niter=1, b=255, top=False):
    # print(f"makeflag: s={size} n={niter}")
    clr = makeRWB(size // 3, b)
    startp = len(pix) - (size * niter) if top else 0
    for i in range(niter):
        for j in range(len(clr)):
            pix[startp + j + (i * len(clr))] = clr[j]
    pix.write()
    return size * niter


def _cycle_rng(pix, ct=60, top=False):
    startp = len(pix) - ct if top else 0
    po = pix[startp]
    for i in range(ct - 1):
        pix[i + startp] = pix[i + startp + 1]
    pix[startp + ct - 1] = po
    pix.write()


class effect_panel:
    def __init__(self, pix, width, height, ledblock=10, debug=False):
        # Create the StateMachine with the ws2812 program
        self._pix = pix
        self.npix = len(pix)
        self.flagsize = 0

        # Initialise the LED array to all off
        self._width = width
        self._height = height
        self._ledblock = ledblock
        # self._strip = array.array(
        #    "I", [0 for _ in range(width * height)]
        # )  # GRB colour order
        self._pix.fill((0, 0, 0))

        # Initialise a counter for the beacon and strobe functions
        self._count = 0
        gc.collect()

    def __str__(self):
        rv = f"led_panel: statemachine:{self._pix}  ({self._width},{self._height}) block={self._ledblock}"
        return rv

    def __del__(self):
        # TODO - tidy up the state machine
        pass

    def __repr__(self):
        # TODO - encode the class state - including which PIO
        pass

    def flag(self, size=24, niter=2, brightness=255, debug=False, top=False):
        if self.flagsize == 0:
            self.flagsize = _makeflag(
                self._pix, size=size, niter=niter, b=brightness, top=top
            )
            print(f"flag: sz={size} n={niter} --> {self.flagsize}")
        else:
            _cycle_rng(self._pix, self.flagsize, top=top)

    def firelight(
        self,
        brightness=255,
        red=255,
        green=64,
        blue=10,
        speed=128,
        fade=255,
        top=True,
        debug=False,
    ):
        """Create a fire-like effect on an LED panel"""
        fade_r = 224 * fade  # How quickly the redness fades
        fade_g = 192 * fade  # How quickly the greenness fades
        fade_b = 128 * fade  # How quickly the blueness fades
        leds_per_block = self._ledblock
        firelen = self._width * self._height
        blocks = firelen // leds_per_block
        pixstart = max(0, self.npix - firelen) if top else 0
        pixend = pixstart + firelen
        # strip = self._strip
        if debug:
            print("fire: " + self.__str__())
            print(f"b={brightness} flen={firelen} pstart={pixstart} pend={pixend}")
        # First fade everything out slightly
        for led in range(pixstart, pixend):
            # Read the current colour
            R, G, B = self._pix[led]

            # Fade it a little bit
            R = (R * fade_r) >> 16
            G = (G * fade_g) >> 16
            B = (B * fade_b) >> 16

            # Write the colour back to the strip
            self._pix[led] = (R, G, B)
        if debug:
            print(f"{leds_per_block} * {blocks}")

        # Occasionally brighten some blocks up
        if randint(0, 255) <= speed:
            if debug:
                print(f"fire update: nblk={blocks * 3 // 4}")
            try:
                # Only brighten about three-quarters of the blocks each time
                for block in range(blocks * 3 // 4):
                    try:
                        # Pick a block at random
                        start_led = pixstart + (randint(0, blocks - 1) * leds_per_block)
                        end_led = start_led + leds_per_block
                        # Pick a random intensity and colour for each block
                        R = randint(red // 8, red)  # Must be at least half of Red
                        G = randint(
                            min(R // 16, green // 4), min(R // 8, green)
                        )  # Can't be more # TODO:han half of R
                        B = randint(
                            min(G // 16, blue // 4), min(G // 8, blue)
                        )  # Can't be more than an eighth of G

                        # Apply the master brightness factor
                        R = (R * brightness) >> 8
                        G = (G * brightness) >> 8
                        B = (B * brightness) >> 8

                        for led in range(start_led, end_led):
                            self._pix[led] = (R, G, B)
                    except Exception as e:
                        print(f"fire update: exception {e}")
                        print(f"             {start_led}, {end_led}")
                        break
            except Exception as e:
                print(f"in update main exception: {e}")

    def beacon(self, brightness=255, red=255, green=64, blue=10, speed=128, stripe=10):
        # Merge the overall brightness into the RGB values
        R = int(red * brightness / 255)
        G = int(green * brightness / 255)
        B = int(blue * brightness / 255)
        # value = (B & 0xFF) + ((R & 0xFF) << 8) + ((G & 0xFF) << 16)

        # Increment the count
        self._count += speed * 4

        offset = (self._count // 255) % self._width
        if offset == 0:
            self._count = 0

        # Convert the stripe width from 0-255 into 1-width
        stripe = ((stripe * self._width) // 255) + 1

        # Set all of the LEDs to the calculated colour
        for led in range(len(self._pix)):
            column = led // self._height

            if (column + offset) % self._width < stripe:
                self._pix[led] = (R, G, B)
            else:
                self._pix[led] = (0, 0, 0)

    def strobe(self, brightness=255, red=255, green=64, blue=10, speed1=10, speed2=100):
        # Increment the count
        self._count += 1
        if self._count > (speed1 + speed2) / 8:
            self._count = 0

        if self._count < speed1 / 8:
            # Merge the overall brightness into the RGB values
            R = int(red * brightness / 255)
            G = int(green * brightness / 255)
            B = int(blue * brightness / 255)
            value = (R, G, B)
        else:
            value = (0, 0, 0)

        # Set all of the LEDs to the calculated colour
        for led in range(len(self._pix)):
            self._pix[led] = value

    def update(self):
        self._pix.write()
        if pixreal:
            sleep_ms(10)
        else:
            sleep(
                0.010
            )  # Make sure there is some dead time before re-triggering the PIO

    def fill(self):
        self._pix.fill((0, 0, 0))
        self._pix.write()

    def fclose(self):
        if not pixreal:
            self._pix.fclose()
