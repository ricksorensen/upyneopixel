import time


def chkssid(wlan):
    wlan.active(True)
    # acthost={}
    hosts = wlan.scan()
    maxstrength = [-1000, "NONET"]
    for h in hosts:
        if "RJS" in h[0]:
            # acthosts[h[0]] = h[3]
            if h[3] > maxstrength[0]:
                maxstrength[0] = h[3]
                maxstrength[1] = h[0]
    print(f"chkssid: {maxstrength}")
    return maxstrength[1]


def connect(ssid="RJSNG_24", key="december23", timeout=30000):
    import network

    sta_if = network.WLAN(network.STA_IF)
    tout = False
    if not sta_if.isconnected():
        print("restarting network connection")
        if ssid is None:
            ssid = chkssid(sta_if)
        sta_if.active(True)
        sta_if.connect(ssid, key)
        tstart = time.ticks_ms()
        while not sta_if.isconnected():
            if time.ticks_diff(time.ticks_ms(), tstart) > timeout:
                tout = True
                break
            time.sleep(1)  # wait till connection
    if tout:
        print(f"network {ssid} not connected")
        sta_if.disconnect()
    else:
        print(f"network {ssid} config:", sta_if.ifconfig())


def connectIP(ssid="RJSNG_24", key="december23", timeout=30000, myIP="192.168.1.177"):
    import network

    sta_if = network.WLAN(network.STA_IF)
    tout = False
    # if machine.reset_cause() != machine.SOFT_RESET:
    #    if myIP is not None:
    #        sta_if.ifconfig((myIP, "255.255.255.0", "192.168.1.18", "8.8.8.8"))
    if not sta_if.isconnected():
        print("restarting network connection")
        sta_if.active(True)
        if myIP is not None:
            sta_if.ifconfig((myIP, "255.255.255.0", "192.168.1.18", "8.8.8.8"))
        if ssid is None:
            ssid = chkssid(sta_if)
        sta_if.connect(ssid, key)
        tstart = time.ticks_ms()
        while not sta_if.isconnected():
            if time.ticks_diff(time.ticks_ms(), tstart) > timeout:
                tout = True
                break
            time.sleep(1)  # wait till connection
        with open("usedssid", "w") as f:
            f.write(f"used SSID={ssid}  connected={not tout}")
        print(f"used SSID={ssid}  connected={not tout}")
    elif myIP is not None and sta_if.ifconfig()[0] != myIP:
        print("resetting IP address from {} to {}".format(sta_if.ifconfig()[0], myIP))
        sta_if.ifconfig((myIP, "255.255.255.0", "192.168.1.18", "8.8.8.8"))
    if tout:
        print(f"network {ssid} not connected")
        sta_if.disconnect()
    else:
        print(f"network {ssid} config:", sta_if.ifconfig())
    return not tout


def dowrepl(ssid="RJSNG_24", key="december23", myIP="192.168.1.174"):
    import webrepl

    print("dowrepl ", myIP)
    rv = connectIP(ssid=ssid, key=key, myIP=myIP)
    if rv:
        webrepl.start()
    return rv
