from umqtt.simple import MQTTClient
import time

dostop = False


def donet():
    import netconnect

    netconnect.connect()


def sub_cb(topic, msg):
    global dostop
    dostop = b"stop" in msg
    # print(f"Topic: {topic} --> {msg}")


# remember to send message as retained
def checkstop(topic=b"alert/control"):
    global dostop
    dostop = False
    mqttc = MQTTClient("esp32c3xiaoUniq", "192.168.1.88")
    mqttc.set_callback(sub_cb)
    mqttc.connect()
    mqttc.subscribe(topic)
    ts = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), ts) < 10000:
        mqttc.check_msg()
        if dostop:
            # reset message
            mqttc.publish(topic, b"okay", retain=True)
            break
        time.sleep(1)
    mqttc.disconnect()
    return dostop
