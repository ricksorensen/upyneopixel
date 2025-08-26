_IP_ADDR = "192.168.1.178"
_LONG_DUR = 200
_TWINK_DUR = 100
_NUM_PIX = 300
_HAN_DUR = 100
_NEOPIN = 1  # XIAO Pin1   C3 GPIO2   S3 GPIO1
_USE_NETWORK = True
_WAIT_NO_CONNECT = 120  # 7200  # 2 hours
_USE_DATE = None  # (2024, 10, 31)  # (2024, 12, 10)
_TEMP_CORRECT = 20
_SWAPRGB = False
_TEMP_PIN = 43  # xiao pin 7: esp32c3 GPIO21 S3 GPIO43

_LDR_PIN = 3  # xiao pin 3: esp32c3 GPIO04    S3 GPIO3
_LDR_DARKUV = 1100000  # 1100000 for dark # microvolt to define on dark level
_LDR_TURNON = 170000
_LDR_REPORT = True

# If True, use LDR to determine on/off
#    False, use TOD to determing on/off
_DAYNIGHT_ON = True
_DEFAULT_BRIGHT = None

_DEEPSLEEP = 0.5  # check every 30 minutes
_DSLEEP_START = 17  # Time to wake from sleep , fractional hour, local STANDARD time
_DSLEEP_STOP = 23
_RANDOM_RATIO = 10
_USEBITBANG = False
_DEBUG = False
_SUFFIX = "178s3"

# effects
_FIRETOP = None
_EVERYDAY_OPT = "FFNUM=30, TEMP, RAND, FWORK"
# _EVERYDAY_OPT = "FWORK"
