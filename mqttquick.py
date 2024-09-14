import machine
import time
import holiday
import runleds

from umqtt.simple import MQTTClient


def msgalert(hrsleep, hrnow):
    msg = "{}: Sleep={}".format(hrnow, hrsleep)
    topic = "alert/sleep" if hrsleep is not None else "alert/wake"
    mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
    mqttc.connect()
    mqttc.publish(topic, msg, retain=True)
    mqttc.disconnect()


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


def check_sleep(dosleep=False, start=None, npix=300, pixpin=2):
    dt = holiday.rjslocaltime(tzoff=-6)  # time.localtime()
    hrsleep = 8 * 3600 * 1000
    hrnow = dt[3] + (dt[4] / 60)
    stime = getstart_time(start)
    print(f" {dt}.   DS {stime}")
    if hrnow < stime:
        hrsleep = int(min(8, stime - hrnow) * 3600 * 1000)
    elif dt[3] < 23:
        hrsleep = 0
    if dosleep and (hrsleep > 0):
        print(f"deepsleep active {hrsleep}")
        if npix is not None:
            pix = runleds.test_setup(npix, pin=pixpin)
            pix.fill((0, 0, 0))
            pix.write()
        msgalert(hrsleep, hrnow)
        time.sleep(0.2)
        machine.deepsleep(hrsleep)
    else:
        print(f"deepsleep request {dosleep} {hrsleep}")
    return hrsleep
