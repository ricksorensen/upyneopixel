import os

if "nostart" not in os.listdir():
    import startholiday as sh

    sh.start(delayStart=2, interruptStart=False)
