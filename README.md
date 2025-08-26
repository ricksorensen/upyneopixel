# upyneopixel
Light show for the yard.

Pixel Strips I have:

- [WS2812BWaterproof](https://www.amazon.com/gp/product/B07P7WWRVH/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1 "60LED/m 5m long, waterproof")
300LEDs, 60LED/m, 5m long
Color order: GRB
-  [WS2812BIndoors](https://www.amazon.com/gp/product/B088BPGMXB/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1 "60LED/m, 5m long")
300 LEDs, 60LED/m, 5m long
Color order: GRB
- [WS2812BIndoorsShort](https://www.amazon.com/gp/product/B09PBGZMNS/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1 "144LED/m, 1m long")
144 LEDs, 144LED/m, 1m long
Color order: GRB
- [WS2811Waterproof](https://www.amazon.com/gp/product/B01AG923GI/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1 "12.5LED/m, 4m long")
50L LEDs, 12.5LED/m, 4m long
Color order: RGB

Example `config.py` file.  `buildconfig.py` is a simple utility to build a config file.
```
_IP_ADDR = "192.168.1.174"
_LONG_DUR = 200
_TWINK_DUR = 100
_NUM_PIX = 120
_HAN_DUR = 100
_NEOPIN = 2
_USE_NETWORK = False
_WAIT_NO_CONNECT = 120  
_USE_DATE = None  # (2024, 10, 30)  # None  # (2024, 12, 10)
_TEMP_CORRECT = 20
_SWAPRGB = False
_TEMP_PIN = 21  # xiao pin 7: esp32c3 GPIO21
_DEEPSLEEP = False
_DSLEEP_START = 18.1  # Time to wake from sleep , fractional hour, local STANDARD time
_RANDOM_RATIO = None
```
 *  `_IP_ADDR` :  assigned IP address if network active.  If `None` use DHCP
 *  `_LONG_DUR`:  number interations of long events
 *  `_TWINK_DUR`: number interations of twinle event
 *  `_NUM_PIX` : number of LEDs in string
 *  `_HAN_DUR`: number of interations of short events
 *  `_NEOPIN`: number/name of machine.Pin to use
 *  `_USE_NETWORK`: boolean, whether to use network interface
 *  `_WAIT_NO_CONNECT`: how long to wait for network connection if enabled
 *  `_USE_DATE`: (year,mon,day) tuple if specific date desire.  If None, use ntp date if network available, else arbitrary date.
 *  `_TEMP_CORRECT`: internal esp32 temp correction factor.  
Not used if external temperature sensor available or not an ESP32.
 *  `_SWAPRGB`: boolean whether to swap red and green in neopixel values
 *  `_TEMP_PIN`: pin with external temperature sensor
 *  `_DEEPSLEEP`: boolean whether to us `deepsleep()` while waiting for start time
 *  `_DSLEEP_START`: Time to wake from sleep , in hour, local STANDARD time. For example 18.5 is 6:30PM local standard time
 *  `_RANDOM_RATIO`: integer to determine frequency of random color insertion. If `None` do not use.   
`1/_RANDOM_RATIO` will be the rate LEDS are randomly set.


Known holidays (summer holidays omitted until solar can provide power!)

+ Valentines day.  Red and white effects
+ St Patricks day.  Green and white effects
+ Halloween.  Floating and or flying eyes, orange
+ Hanukkah.  Blue and white effects
+ Christmas.  Red and green effects
+ Various birthdays.

Define2
:  Does this work?

