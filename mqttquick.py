import config  # makesur config is global instance
import time
import holiday
import logging
from umqtt.simple import MQTTClient

logger = logging.getLogger(__name__)


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
    try:
        mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
        mqttc.connect()
        mqttc.publish(topic, msg, retain=True)
        mqttc.disconnect()
        logger.debug(f"msgalert: {msg} -> {topic}")
    except Exception as connerr:
        logger.exception("msgalert: mqtcc connection error", exc_info=connerr)


def msgspecial(msgin, topic):
    tnow = holiday.rjslocaltime(tzoff=-6)
    msg = (
        "{:04d}{:02d}{:02d}{:02d}{:02d}: ".format(
            tnow[0], tnow[1], tnow[2], tnow[3], tnow[4]
        )
        + msgin
    )
    try:
        mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
        mqttc.connect()
        mqttc.publish(topic, msg, retain=True)
        mqttc.disconnect()
    except Exception as connerr:
        logger.exception("msgspecial: mqtcc connection error", exc_info=connerr)


_controlstate = 0


def _sub_cb(topic, msg):
    global _controlstate
    if b"stop" in msg:
        _controlstate = 0x01
        if "hard" in msg:
            _controlstate = 0x05
    elif b"start" in msg:
        _controlstate = 0x02
        if "hard" in msg:
            _controlstate = 0x06
    else:  # if b"okay" in msg:
        _controlstate = 0x00
    # print(topic + " sub_cb " + msg)


# remember to send message as retained
def checkcontrol(topic=b"alert/control"):
    newcontrol = _controlstate
    try:
        mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88")
        mqttc.set_callback(_sub_cb)
        mqttc.connect()
        mqttc.subscribe(topic)
        ts = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), ts) < 3000:
            mqttc.check_msg()
            if _controlstate != newcontrol:
                newcontrol = _controlstate
                if newcontrol & 0x04 == 0:
                    mqttc.publish(topic, b"okay", retain=True)
                break
            time.sleep(0.5)
        mqttc.disconnect()
    except Exception as connerr:
        logger.exception("checkcontrol: mqtcc connection error", exc_info=connerr)
    # print(f"checkcontrol stop={dostp}  start={dostr}")
    return newcontrol & 0x03


def sendmsg(msg, topic=b"alert/message", addtopic=""):
    try:
        mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88", keepalive=60)
        mqttc.connect()
        mqttc.publish(topic + addtopic, msg, retain=True)
        mqttc.disconnect()
    except Exception as connerr:
        logger.exception("sendmsg: mqtcc connection error", exc_info=connerr)


def _sub_np(topic, msg):
    if b"EYEGAP" in topic:
        config._EYEGAP = int(msg)
    elif b"NEYES" in topic:
        config._NEYES = int(msg)
    elif b"FLYRATE" in topic:
        config._FLYRATE = float(msg)
    elif b"EVERYDAY_OPT" in topic:
        config._EVERYDAY_OPT = msg
    elif b"DSLEEP_START" in topic:
        config.DSLEEP_START = float(msg)
    elif b"DEBUG" in topic:
        config._DEBUG = "True" in msg
    elif b"CHECK" in topic:
        print("CHECK")
    # print(f" Incoming: {topic} -> {msg}")


_config_mqtt = None


# remember to send message as retained
def checkconfig(done=False):
    global _config_mqtt
    if config._USE_NETWORK:
        if done:
            if _config_mqtt is not None:
                _config_mqtt.disconnect()
            _config_mqtt = None
        else:
            try:
                if _config_mqtt is None:
                    _config_mqtt = MQTTClient("esp32c3xiaoCfig", "192.168.1.88")
                    _config_mqtt.set_callback(_sub_np)
                    _config_mqtt.connect()
                    _config_mqtt.subscribe(topic=b"neopixel/#")
                while _config_mqtt.check_msg() is not None:
                    time.sleep(0.001)
            except Exception as connerr:
                _config_mqtt = None
                logger.exception(
                    "checkconfig: mqtcc connection error", exc_info=connerr
                )
