import holiday
import mqttquick
import time
import config
import machine
import random

try:
    import esp32

    # wdt=machine.WDT(timeout=10*60*1000)
    # wdt.feed()

    def getlightlevel():
        chklight = machine.ADC(
            machine.Pin(config._LDR_PIN), atten=machine.ADC.ATTN_11DB
        )
        light_uv = 0
        for _ in range(20):
            light_uv = chklight.read_uv()
        if config._LDR_REPORT:
            mqttquick.msgspecial(f"{light_uv}", "alert/lightval" + config._SUFFIX)
        return light_uv

    def getBrightness():
        bright = config._DEFAULT_BRIGHT
        if bright is None:
            lvl = getlightlevel()
            if lvl > config._LDR_DARKUV:
                bright = 0.1
            elif lvl > 700000:
                bright = 0.3
            else:
                bright = 0.6
        return bright

    def check_sleep_light(
        pix, dosleep=0.25, start=None, stop=23, everydayu=None, debug=False
    ):
        dsleept = dosleep if dosleep is not None else 0.25
        dt = holiday.rjslocaltime(tzoff=-6)  # time.localtime()
        hrsleep = int(dsleept * 3600 * 1000)
        hrnow = dt[3] + (dt[4] / 60)
        # stime = mqttquick.getstart_time(start)
        # print(f" {dt}.   DS {stime}")
        light = getlightlevel()
        if (light > config._LDR_DARKUV) and (8 < hrnow < stop):
            hrsleep = 0
        temp = None
        if pix is not None:
            pix.fill((0, 0, 0))
            if ((hrnow < 8.5) or (hrnow > 15.5)) and (everydayu is not None):
                c, temp = everydayu.getTempColor(b=getBrightness())
                print("Setting day temp  ", c)
                lp = random.randint(0, len(pix) - 60)
                for i in range(lp, lp + 60):
                    pix[i] = c
            else:
                print("no everydayu passed")
            if hrsleep > 0:
                pix.write()
        if (dosleep is not None) and (hrsleep > 0):
            print(f"deepsleep active {hrsleep} {temp}")
            # endstat.append("deepsleep active")
            mqttquick.msgalert(hrsleep, hrnow, temp=temp, addtopic=config._SUFFIX)
            time.sleep(0.2)
            if not debug:
                machine.deepsleep(hrsleep)
            hrsleep = -1
        else:
            print(f"deepsleep request {dosleep} {hrsleep} {temp}")
        # wdt.feed()
        return hrsleep

    def getstart_time(start):
        rv = start
        if rv is None:
            dt = holiday.rjslocaltime(tzoff=-6)
            if (dt[1] > 10) or (dt[1] < 4):
                rv = 17
            elif (dt[1] > 8) or (dt[1] < 6):
                rv = 18
            else:
                rv = 19
        return rv

    def check_sleep_time(
        pix, dosleep=0.25, start=None, stop=23, everydayu=None, debug=False
    ):
        dsleept = dosleep if dosleep is not None else 0.25
        dt = holiday.rjslocaltime(tzoff=-6)  # time.localtime()
        hrsleep = int(dsleept * 3600 * 1000)
        hrnow = dt[3] + (dt[4] / 60)
        stime = getstart_time(start)
        print(f" {dt}.   DS {stime}")
        if hrnow < stime:
            hrsleep = int(min(dsleept, stime - hrnow) * 3600 * 1000)
        elif hrnow < stop:  # assumes stop not past midnight
            hrsleep = 0
        temp = None
        _ = getlightlevel()
        if pix is not None:
            pix.fill((0, 0, 0))
            if ((hrnow < 8.5) or (hrnow > 15.5)) and (everydayu is not None):
                c, temp = everydayu.getTempColor(b=0.1)
                print("Setting day temp  ", c)
                lp = random.randint(0, len(pix) - 60)
                for i in range(lp, lp + 60):
                    pix[i] = c
            else:
                print("no everydayu passed")
            if hrsleep > 0:
                pix.write()
        if (dosleep is not None) and (hrsleep > 0):
            print(f"deepsleep active {hrsleep} {temp}")
            # endstat.append("deepsleep active")
            mqttquick.msgalert(hrsleep, hrnow, temp=temp, addtopic=config._SUFFIX)
            time.sleep(0.2)
            if not debug:
                machine.deepsleep(hrsleep)
            hrsleep = -1
        else:
            print(f"deepsleep request {dosleep} {hrsleep} {temp}")
        # wdt.feed()
        return hrsleep

    # esp32.RMT.bitstream_channel(0)  # default is 1
    # esp32.RMT.bitstream_channel(None)  # use bitbanging
    if config._USEBITBANG:
        esp32.RMT.bitstream_channel(None)
except ImportError:

    def check_sleep_light(pix, dosleep=False, start=None, stop=23, everydayu=None):
        return 0

    def check_sleep_time(pix, dosleep=False, start=None, stop=23, everydayu=None):
        return 0


def setCheckStart(lightSensor=False):
    return check_sleep_light if lightSensor else check_sleep_time
