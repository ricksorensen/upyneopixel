import logging

logging.basicConfig(
    filename="rjslogx.log",
    level=logging.ERROR,
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
ch.setFormatter(
    logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s"
    )
)
logging.getLogger().addHandler(ch)

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

logger = logging.getLogger(__name__)


def start(
    interruptStart=True,
    delayStart=0,
    *,
    force_date=None,
    fixtemp=None,
    debug=False,
    loglevel=None,
):
    if loglevel is not None:
        logging.changeLevel(loglevel)
    logger.info("starting lights")
    if interruptStart:
        print("time start up interrupt")
        time.sleep(60)
    allokay = False
    hardsleep = config._DEEPSLEEP  # should read from config.py
    starttime = config._DSLEEP_START
    check_sleep = checkstart.setCheckStart(lightSensor=config._DAYNIGHT_ON)

    if config._USE_NETWORK:
        logger.debug("starting webrepl " + config._IP_ADDR)
        allokay = netconnect.dowrepl(ssid=None, myIP=config._IP_ADDR)
        # allokay = netconnect.doviperide(myIP=config._IP_ADDR)
        logger.warning(f"net status: {allokay}")
        config._USE_NETWORK = allokay
        if allokay:
            controlmsg = mqttquick.checkcontrol("alert/control" + config._SUFFIX)
            if controlmsg & 0x01 == 1:
                endstat.append("Stopped by mqtt message")
                logger.error("Stopped by mqtt message")
                logging.shutdown()
                return endstat
            elif controlmsg & 0x02 == 2:
                # hardsleep = None
                starttime = 0
                check_sleep = checkstart.setCheckStart(lightSensor=False)
                logger.debug("Forcing pattern start from mqtt message")
            while allokay and (delayStart > 0) and (os.dupterm(None) is None):
                # print("wait for WebREPL connection")
                time.sleep(30)
                delayStart = delayStart - 1
        allokay = True
    else:
        allokay = True
        endstat.append("no network requested")
    endstat.append(f"network allok:{allokay}")
    logger.info(f"starting light: mem {gc.mem_free()} network {not allokay}")
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
                        ntptime.timeout = 100
                        try:
                            ntptime.settime()
                            retry = 0
                            logger.error("Set date from ntp")
                            endstat.append("set ntp date")
                        except Exception as ntpexcept:
                            endstat.append(f"ntp timeout {retry}")
                            endstat.append(ntpexcept)
                            logger.exception(endstat[2], exc_info=ntpexcept)
                            if retry == 0:
                                pix.fill((0, 0, 0))
                                pix.write()
                                # fall through and use prior RTC setting
                                # raise ntpexcept
                                logger.error("Failed ntp set date")
                dt = holiday.rjslocaltime(tzoff=-6)
                endstat.append(f"set date {dt}")

            else:
                import machine

                r = machine.RTC()
                if force_date is None:
                    force_date = (
                        (1999, 1, 2) if config._USE_DATE is None else config._USE_DATE
                    )
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
            logger.info(endstat[-1])
            stoptime = config._DSLEEP_STOP if hasattr(config, "_DSLEEP_STOP") else 23
            brightlevel = checkstart.getBrightness()
            mqttquick.checkconfig()
            effects = [
                holiday.NoDate(
                    pix,
                    dur=config._HAN_DUR,
                    nrandom=(
                        (len(pix) // config._RANDOM_RATIO)
                        if config._RANDOM_RATIO is not None
                        else None
                    ),
                    bright=brightlevel,
                ),
                holiday.Birthday(pix, dur=config._LONG_DUR, bright=brightlevel),
                holiday.Valentine(
                    pix,
                    dur=config._HAN_DUR,
                    nrandom=None,
                    bright=brightlevel,
                ),
                holiday.SaintPatrick(
                    pix,
                    dur=config._HAN_DUR,
                    nrandom=None,
                    bright=brightlevel,
                ),
                holiday.Hanukkah(
                    pix,
                    dur=config._HAN_DUR,
                    nrandom=(
                        (len(pix) // config._RANDOM_RATIO)
                        if config._RANDOM_RATIO is not None
                        else None
                    ),
                    bright=brightlevel,
                ),
                holiday.Christmas(
                    pix,
                    dur=config._LONG_DUR,
                    nrandom=(
                        (len(pix) // config._RANDOM_RATIO)
                        if config._RANDOM_RATIO is not None
                        else None
                    ),
                    bright=brightlevel,
                ),
                halloween.Halloween(
                    pix,
                    bright=brightlevel,
                    dur=config._LONG_DUR,
                    gap=config.__dict__.get("_EYEGAP", 1),
                    neyes=config.__dict__.get("_NEYES", 5),
                ),
                fire.Fire(
                    pix,
                    dur=config._LONG_DUR * 1000,  # ms
                    update=25,
                    top=config._FIRETOP,
                    fw=None,
                    debug=debug,
                ),
                everyday.Aprilfool(
                    pix,
                    dur=config._LONG_DUR,
                    fixtemp=35,
                    nrandom=(
                        (len(pix) // config._RANDOM_RATIO)
                        if config._RANDOM_RATIO is not None
                        else None
                    ),
                    bright=brightlevel,
                ),
            ]
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
                logger.warning("Deepsleep as directed before running")
                logging.shutdown()
                return endstat
            hardsleep = config._DEEPSLEEP
            gc.collect()
            logger.warning(f"Start memory  {gc.mem_free()}")
            print(f"Start memory  {gc.mem_free()}")
            endstat.append("holidays created")
            while True:
                mqttquick.checkconfig()
                gc.collect()
                brightlevel = checkstart.getBrightness()
                logger.debug(f"Brightness: {brightlevel}")
                if not any(
                    eft.chkDate(dt, run=True, bright=brightlevel) for eft in effects
                ):
                    fallback.run(
                        correct=config._TEMP_CORRECT,
                        bright=brightlevel,
                    )
                gc.collect()
                logger.info(f"effect done: {gc.mem_free()}")
                print("effect done: ", gc.mem_free())
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
                    logger.error("DeepSleep .. Debug unexpected after effect")
                    logging.shutdown()
                    return endstat
        except Exception as unexpected:
            import sys

            endstat.append("Unexpected Exception")
            endstat.append(str(unexpected))
            with open("exception.oops", "a") as f:
                sys.print_exception(unexpected, f)
            logger.exception(" unexpected exception ", exc_info=unexpected)
            pix.fill((0, 0, 0))
            pix.write()
            if config._USE_NETWORK:
                mqttquick.sendmsg(endstat[-1], addtopic=config._SUFFIX)
            time.sleep(0.2)
            checkstart.cpusleep(1800000)  # 1 minute try again
        except KeyboardInterrupt:
            print("Keyboard Interrupt handled")
            endstat.append("KeyboardInterrupt")
            logger.exception(" Keyboard Interrupt")
            pix.fill((0, 0, 0))
            pix.write()
            if config._USE_NETWORK:
                mqttquick.sendmsg(endstat[-1], addtopic=config._SUFFIX)
    else:
        # print("Not All OKAY")
        endstat.append("Not ALL OKAY")
        logger.error(" not good not starting")
    if config._USEBITBANG:
        esp32.RMT.bitstream_channel(1)
    logger.warning(f"All done: {endstat}")

    logging.shutdown()
    mqttquick.checkconfig(done=True)
    return endstat
