_IP_ADDR = "192.168.1.177"
_LONG_DUR = 15
_TWINK_DUR = 15
_NUM_PIX = 120
_HAN_DUR = 15
_NEOPIN = 1  # 2 for C3, 1 for S3
_USE_NETWORK = True
_WAIT_NO_CONNECT = 30  # 7200  # 2 hours
_USE_DATE = None  # (2025, 4, 1)  # (2024, 10, 31)  # (2024, 12, 10)
_TEMP_CORRECT = 20
_SWAPRGB = False
_TEMP_PIN = 43  # xiao pin 7: esp32c3 GPIO21   esp32s3: GPIO43
_LDR_PIN = 3  # xiao pin 2: esp32c3 GPIO04 GPIO3 3 for S3
_LDR_DARKUV = 1500000  # microvolt to define on dark level
_LDR_TURNON = 2000
_LDR_REPORT = True

# If True, use LDR to determine on/off
#    False, use TOD to determing on/off
_DAYNIGHT_ON = False
_DEFAULT_BRIGHT = None

_DEEPSLEEP = 0.05  # hour maximum deep sleep time before checking
# None if no deepsleep
_DSLEEP_START = 8  # Time to wake from sleep , fractional hour, local STANDARD time
_DSLEEP_STOP = 23.5
_RANDOM_RATIO = None
_USEBITBANG = False
_DEBUG = True
_LOGLEVEL = "warn"  # error, warn, info, debug default is error
_SUFFIX = "test"

# effects
# FF: Fireflies
# FFNUM=nfireflies
# RAND: Random colors
# TEMP: show temp
# FWORK: use fireworks
_FIRETOP = None
_EVERYDAY_OPT = "FF, RAND"
_CHRISTMAS_OPT = "FFNUM=5, TWINKLE, STREAM"
# _EVERYDAY_OPT = "FWORK"

# Halloween
_EYEGAP = 2
_NEYES = None
_FLYRATE = 1  # seconds
