import holiday
import everyday
import mqttquick
import halloween
import fire
import runleds
import time
import os
import gc
import config
import checkstart
import esp32

endstat = []


if config._USE_NETWORK:
    import netconnect
    import ntptime


def start(
    interruptStart=True, delayStart=0, force_date=None, fixtemp=None, debug=False
):
    if interruptStart:
        print("time start up interrupt")
        time.sleep(60)
    allokay = False
    hardsleep = config._DEEPSLEEP  # should read from config.py
    starttime = config._DSLEEP_START
    check_sleep = checkstart.setCheckStart(lightSensor=config._DAYNIGHT_ON)

    if config._USE_NETWORK:
        print("starting webrepl ", config._IP_ADDR)
        allokay = netconnect.dowrepl(myIP=config._IP_ADDR)
        # allokay = netconnect.doviperide(myIP=config._IP_ADDR)
        print("net status: ", allokay)
        controlmsg = mqttquick.checkcontrol("alert/control" + config._SUFFIX)
        if controlmsg & 0x01 == 1:
            endstat.append("Stopped by mqtt message")
            return endstat
        elif controlmsg & 0x02 == 2:
            # hardsleep = None
            starttime = 0
            check_sleep = checkstart.setCheckStart(lightSensor=False)
            print("Forcing pattern start from mqtt message")
        while allokay and (delayStart > 0) and (os.dupterm(None) is None):
            print("wait for WebREPL connection")
            time.sleep(30)
            delayStart = delayStart - 1
    else:
        allokay = True
        endstat.append("no network requested")
    endstat.append(f"network allok:{allokay}")
    print("starting lights")
    print("initial memory ", gc.mem_free())
    if allokay:
        try:
            pix = runleds.test_setup(
                config._NUM_PIX, pin=config._NEOPIN, swaprgb=config._SWAPRGB
            )
            if force_date is None and config._USE_DATE is None:
                if config._USE_NETWORK:
                    time.sleep(5)
                    retry = 5
                    while retry > 0:
                        retry = retry - 1
                        ntptime.timeout = 5
                        try:
                            ntptime.settime()
                            retry = 0
                            endstat.append("set ntp date")
                        except Exception as ntpexcept:
                            print("ntp timeout")
                            endstat.append(f"ntp timeout {retry}")
                            endstat.append(ntpexcept)
                            if retry == 0:
                                pix.fill((0, 0, 0))
                                pix.write()
                                raise ntpexcept
                dt = holiday.rjslocaltime(tzoff=-6)
                endstat.append(f"set date {dt}")

            else:
                import machine

                r = machine.RTC()
                if force_date is None:
                    force_date = config._USE_DATE
                r.datetime(
                    (
                        force_date[0],
                        force_date[1],
                        force_date[2],
                        0,
                        0,
                        0,
                        0,
                        0,
                    )
                )
                dt = time.localtime()
                endstat.append("RTC time used")
            endstat.append(f"date: {dt}")
            print(dt)
            stoptime = config._DSLEEP_STOP if hasattr(config, "_DSLEEP_STOP") else 23
            brightlevel = checkstart.getBrightness()
            hanukkah = holiday.Hanukkah(
                pix,
                dur=config._HAN_DUR,
                nrandom=(
                    (len(pix) // config._RANDOM_RATIO)
                    if config._RANDOM_RATIO is not None
                    else None
                ),
                bright=brightlevel,
            )
            valentine = holiday.Valentine(
                pix,
                dur=config._HAN_DUR,
                nrandom=None,
                bright=brightlevel,
            )
            stpats = holiday.SaintPatrick(
                pix,
                dur=config._HAN_DUR,
                nrandom=None,
                bright=brightlevel,
            )
            christmas = holiday.Christmas(
                pix,
                dur=config._LONG_DUR,
                nrandom=(
                    (len(pix) // config._RANDOM_RATIO)
                    if config._RANDOM_RATIO is not None
                    else None
                ),
                bright=brightlevel,
            )
            birthday = holiday.Birthday(pix, dur=config._LONG_DUR, bright=brightlevel)
            nyeve = holiday.Birthday(pix, dur=config._LONG_DUR, bright=0.5)
            halloeve = halloween.Halloween(
                pix,
                bright=brightlevel,
            )
            dofire = fire.Fire(
                pix,
                dur=config._LONG_DUR * 1000,  # ms
                update=25,
                top=config._FIRETOP,
                fw=None,
                debug=debug,
            )
            aprilfool = everyday.Aprilfool(
                pix,
                dur=config._LONG_DUR,
                fixtemp=35,
                nrandom=(
                    (len(pix) // config._RANDOM_RATIO)
                    if config._RANDOM_RATIO is not None
                    else None
                ),
                bright=brightlevel,
            )
            fallback = everyday.Everyday(
                pix,
                dur=config._LONG_DUR,
                fixtemp=fixtemp,
                nrandom=(
                    (len(pix) // config._RANDOM_RATIO)
                    if config._RANDOM_RATIO is not None
                    else None
                ),
                bright=brightlevel,
            )
            if (
                check_sleep(
                    pix,
                    dosleep=hardsleep,
                    start=starttime,
                    stop=stoptime,
                    everydayu=fallback,
                    debug=debug,
                )
                < 0
            ):
                endstat.append("DeepSleep .. Debug")
                return endstat
            hardsleep = config._DEEPSLEEP

            print(" Allocate memory :", gc.mem_free())
            endstat.append("holidays created")
            while True:
                brightlevel = checkstart.getBrightness()
                print(f"Brightness: {brightlevel}")
                _ = (
                    dofire.chkDate(dt=dt, run=True, bright=brightlevel)
                    or nyeve.chkDate(dt=dt, run=True)
                    or birthday.chkDate(dt=dt, run=True, bright=brightlevel)
                    or hanukkah.chkDate(dt=dt, run=True, bright=brightlevel)
                    or valentine.chkDate(dt=dt, run=True, bright=brightlevel)
                    or christmas.chkDate(dt=dt, run=True, bright=brightlevel)
                    or stpats.chkDate(dt=dt, run=True, bright=brightlevel)
                    or halloeve.chkDate(dt=dt, run=True, bright=brightlevel)
                    or aprilfool.chkDate(dt=dt, run=True, bright=brightlevel)
                    or fallback.run(
                        correct=config._TEMP_CORRECT,
                        bright=brightlevel,
                    )
                )
                print("free mem: ", gc.mem_free())
                gc.collect()
                if (
                    check_sleep(
                        pix,
                        dosleep=hardsleep,
                        start=starttime,
                        stop=stoptime,
                        everydayu=fallback,
                        debug=debug,
                    )
                    < 0
                ):
                    endstat.append("DeepSleep .. Debug")
                    return endstat
        except Exception as unexpected:
            import sys

            endstat.append("Unexpected Exception")
            endstat.append(str(unexpected))
            sys.print_exception(unexpected)
            pix.fill((0, 0, 0))
            pix.write()
            mqttquick.sendmsg(endstat[-1], addtopic=config._SUFFIX)
    else:
        print("Not All OKAY")
        endstat.append("Not ALL OKAY")

    if config._USEBITBANG:
        esp32.RMT.bitstream_channel(1)

    return endstat
