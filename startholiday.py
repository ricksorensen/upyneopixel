import machine
import holiday
import everyday
import runleds
import time
import os
import gc
import config

try:
    import esp32

    haveTemp = True
except ImportError:
    haveTemp = False

if config._USE_NETWORK:
    import netconnect
    import ntptime


def check_sleep(dosleep=False):
    dt = holiday.rjslocaltime(tzoff=-6)  # time.localtime()
    hrsleep = 8 * 3600 * 1000
    print(f" {dt}.   DS {config._DSLEEP_START}")
    hrnow = dt[3] + (dt[4] / 60)
    if hrnow < config._DSLEEP_START:
        hrsleep = int(min(8, config._DSLEEP_START - hrnow) * 3600 * 1000)
    elif dt[3] < 23:
        hrsleep = 0
    if dosleep and (hrsleep > 0):
        print(f"deepsleep active {hrsleep}")
        time.sleep(0.2)
        machine.deepsleep(hrsleep)
    else:
        print(f"deepsleep request {dosleep} {hrsleep}")
    return hrsleep


endstat = []


def start(interruptStart=True, delayStart=False):
    if interruptStart:
        print("time start up interrupt")
        time.sleep(30)
    allokay = True
    if config._USE_NETWORK:
        print("starting webrepl ", config._IP_ADDR)
        allokay = netconnect.dowrepl(myIP=config._IP_ADDR)
        print("net status: ", allokay)
        if delayStart:
            print("wait for WebREPL connection")
            while os.dupterm(None) is None:
                time.sleep(30)
    print("starting lights")
    print("initial memory ", gc.mem_free())
    if allokay:
        if config._USE_DATE is None:
            if config._USE_NETWORK:
                time.sleep(5)
                ntptime.settime()
            dt = holiday.rjslocaltime(tzoff=-6)
        else:
            import machine

            r = machine.RTC()
            r.datetime(
                (
                    config._USE_DATE[0],
                    config._USE_DATE[1],
                    config._USE_DATE[2],
                    0,
                    0,
                    0,
                    0,
                    0,
                )
            )
            dt = time.localtime()
        print(dt)
        hardsleep = config._DEEPSLEEP  # should read from config.py
        check_sleep(hardsleep)
        pix = runleds.test_setup(config._NUM_PIX, pin=config._NEOPIN)
        if haveTemp:
            tmcu = esp32.mcu_temperature()
            tmcu = esp32.mcu_temperature()
            print("temp ", tmcu)
        else:
            print("no temperature available")

        hanukkah = holiday.Hanukkah(pix, dur=config._HAN_DUR, nrandom=len(pix) // 5)
        valentine = holiday.Valentine(
            pix, dur=config._HAN_DUR, nrandom=None, swaprg=config._SWAPRGB
        )
        stpats = holiday.SaintPatrick(
            pix, dur=config._HAN_DUR, nrandom=None, swaprg=config._SWAPRGB
        )
        christmas = holiday.Christmas(pix, dur=config._LONG_DUR, nrandom=len(pix) // 3)
        birthday = holiday.Birthday(pix, dur=config._LONG_DUR)
        fallback = everyday.Everyday(
            pix,
            dur=config._LONG_DUR,
        )
        print(" Allocate memory :", gc.mem_free())
        try:
            while True:
                didholiday = (
                    birthday.chkDate(dt=dt, run=True)
                    or hanukkah.chkDate(dt=dt, run=True)
                    or valentine.chkDate(dt=dt, run=True)
                    or christmas.chkDate(dt=dt, run=True)
                    or stpats.chkDate(dt=dt, run=True)
                    or fallback.run(
                        correct=config._TEMP_CORRECT, swaprg=config._SWAPRGB
                    )
                )
                print("free mem: ", gc.mem_free())
                if haveTemp:
                    print("temp: ", esp32.mcu_temperature())
                gc.collect()
                check_sleep(hardsleep)
        except Exception as unexpected:
            endstat.append("Unexpected Exception")
            endstat.append(unexpected)
    else:
        print("Not All OKAY")
        endstat.append("Not ALL OKAY")
    return endstat
