waddr=$1
if [[ "$waddr" = "" ]]; then
    waddr=192.168.1.178
fi
echo "path $waddr"
echo "saving in /tmp/fromwebr"

mkdir -p /tmp/fromwebr

webrepl_cli.py -p rick $waddr:boom.py /tmp/fromwebr/boom.py
webrepl_cli.py -p rick $waddr:boot.py /tmp/fromwebr/boot.py
webrepl_cli.py -p rick $waddr:checkstart.py /tmp/fromwebr/checkstart.py 
webrepl_cli.py -p rick $waddr:colorsupport.py /tmp/fromwebr/colorsupport.py 
webrepl_cli.py -p rick $waddr:config.py /tmp/fromwebr/config.remote.py 
webrepl_cli.py -p rick $waddr:cpixels.py /tmp/fromwebr/cpixels.py 
webrepl_cli.py -p rick $waddr:effect_panel.py /tmp/fromwebr/effect_panel.py 
webrepl_cli.py -p rick $waddr:effects.py /tmp/fromwebr/effects.py 
webrepl_cli.py -p rick $waddr:everyday.py /tmp/fromwebr/everyday.py 
webrepl_cli.py -p rick $waddr:fire.py /tmp/fromwebr/fire.py 
webrepl_cli.py -p rick $waddr:fwpartx.py /tmp/fromwebr/fwpartx.py 
webrepl_cli.py -p rick $waddr:halloween.py /tmp/fromwebr/halloween.py 
webrepl_cli.py -p rick $waddr:holiday.py /tmp/fromwebr/holiday.py 
webrepl_cli.py -p rick $waddr:lightning.py /tmp/fromwebr/lightning.py 
webrepl_cli.py -p rick $waddr:main.py /tmp/fromwebr/main.py 
webrepl_cli.py -p rick $waddr:mqttquick.py /tmp/fromwebr/mqttquick.py 
webrepl_cli.py -p rick $waddr:netconnect.py /tmp/fromwebr/netconnect.py 
webrepl_cli.py -p rick $waddr:randBlinkerFade.py /tmp/fromwebr/randBlinkerFade.py 
webrepl_cli.py -p rick $waddr:runleds.py /tmp/fromwebr/runleds.py 
webrepl_cli.py -p rick $waddr:simpfirefly.py /tmp/fromwebr/simpfirefly.py 
webrepl_cli.py -p rick $waddr:startholiday.py /tmp/fromwebr/startholiday.py 
webrepl_cli.py -p rick $waddr:twinkle.py /tmp/fromwebr/twinkle.py 
webrepl_cli.py -p rick $waddr:webrepl_cfg.py /tmp/fromwebr/webrepl_cfg.py 
webrepl_cli.py -p rick $waddr:rjslogx.log /tmp/fromwebr/rjslogx.log
webrepl_cli.py -p rick $waddr:exception.oops /tmp/fromwebr/exception.oops
mkdir -p /tmp/fromwebr/lib
webrepl_cli.py -p rick $waddr:/lib/logging.mpy /tmp/fromwebr/lib/logging.mpy
webrepl_cli.py -p rick $waddr:/lib/time.mpy /tmp/fromwebr/lib/time.mpy

