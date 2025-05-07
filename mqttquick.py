import time
import holiday

from umqtt.simple import MQTTClient


def msgalert(hrsleep, hrnow, temp=None, addtopic=""):
    tnow = holiday.rjslocaltime(tzoff=-6)
    msg = "{:04d}{:02d}{:02d}{:02d}{:02d}: Hrnow={} Sleep={} Temp={}".format(
        tnow[0], tnow[1], tnow[2], tnow[3], tnow[4], hrnow, hrsleep, temp
    )
    topic = (
        f"alert/sleep{addtopic}"
        if ((hrsleep is not None) and (hrsleep > 0))
        else f"alert/wake{addtopic}"
    )
    mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
    mqttc.connect()
    mqttc.publish(topic, msg, retain=True)
    mqttc.disconnect()


def msgspecial(msgin, topic):
    tnow = holiday.rjslocaltime(tzoff=-6)
    msg = (
        "{:04d}{:02d}{:02d}{:02d}{:02d}: ".format(
            tnow[0], tnow[1], tnow[2], tnow[3], tnow[4]
        )
        + msgin
    )
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


_controlstate = 0


def _sub_cb(topic, msg):
    global _controlstate
    if b"stop" in msg:
        _controlstate = 1
    elif b"start" in msg:
        _controlstate = 2
    # print(topic + " sub_cb " + msg)


# remember to send message as retained
def checkcontrol(topic=b"alert/control"):
    global _controlstate
    mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88")
    mqttc.set_callback(_sub_cb)
    mqttc.connect()
    mqttc.subscribe(topic)
    ts = time.ticks_ms()
    newcontrol = _controlstate
    while time.ticks_diff(time.ticks_ms(), ts) < 3000:
        mqttc.check_msg()
        if _controlstate != newcontrol:
            newcontrol = _controlstate
            mqttc.publish(topic, b"okay", retain=True)
            break
        time.sleep(0.5)
    mqttc.disconnect()
    # print(f"checkcontrol stop={dostp}  start={dostr}")
    return newcontrol


def sendmsg(msg, topic=b"alert/message"):
    mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
    mqttc.connect()
    mqttc.publish(topic, msg, retain=True)
    mqttc.disconnect()
