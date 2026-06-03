from time import sleep
from random import randint
import gc
import logging

logger = logging.getLogger(__name__)


class effect:
    def __init__(self, pix, debug=False):
        # Create the StateMachine with the ws2812 program
        self._pix = pix
        self.npix = len(pix)
        self._pix.fill((0, 0, 0))

        gc.collect()

    def __str__(self):
        rv = f"led_panel: statemachine:{self._pix} "
        return rv

    def __del__(self):
        # TODO - tidy up the state machine
        pass

    def __repr__(self):
        # TODO - encode the class state - including which PIO
        pass

    def update(self):
        self._pix.write()
        #        if pixreal:
        #            sleep_ms(10)
        #        else:
        sleep(0.010)  # Make sure there is some dead time before re-triggering the PIO

    def fill(self):
        self._pix.fill((0, 0, 0))
        self._pix.write()
