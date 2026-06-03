waddr=$1
if [[ "$waddr" = "" ]]; then
    waddr=192.168.1.178
fi
echo " copying files to $waddr"

webrepl_cli.py -p rick boom.py $waddr:boom.py
webrepl_cli.py -p rick boot.py $waddr:boot.py
webrepl_cli.py -p rick checkstart.py $waddr:checkstart.py
webrepl_cli.py -p rick colorsupport.py $waddr:colorsupport.py
#webrepl_cli.py -p rick config.py $waddr:config.py
echo "Not copying config.py to remote"
webrepl_cli.py -p rick cpixels.py $waddr:cpixels.py
webrepl_cli.py -p rick effect_panel.py $waddr:effect_panel.py
webrepl_cli.py -p rick effects.py $waddr:effects.py
webrepl_cli.py -p rick everyday.py $waddr:everyday.py
webrepl_cli.py -p rick fire.py $waddr:fire.py
webrepl_cli.py -p rick fwpartx.py $waddr:fwpartx.py
webrepl_cli.py -p rick halloween.py $waddr:halloween.py
webrepl_cli.py -p rick holiday.py $waddr:holiday.py
webrepl_cli.py -p rick lightning.py $waddr:lightning.py
#webrepl_cli.py -p rick main.py $waddr:main.py
echo "Not copying main.py to remote"
webrepl_cli.py -p rick mqttquick.py $waddr:mqttquick.py
webrepl_cli.py -p rick netconnect.py $waddr:netconnect.py
webrepl_cli.py -p rick randBlinkerFade.py $waddr:randBlinkerFade.py
webrepl_cli.py -p rick runleds.py $waddr:runleds.py
webrepl_cli.py -p rick simpfirefly.py $waddr:simpfirefly.py
webrepl_cli.py -p rick startholiday.py $waddr:startholiday.py
webrepl_cli.py -p rick twinkle.py $waddr:twinkle.py
#webrepl_cli.py -p rick webrepl_cfg.py $waddr:webrepl_cfg.py
echo "Not copying webrepl_cfg.py to remote"
echo " need to assure libraries are present:"
echo "    lib/time.py     is present from micropython-lib (includes strftime)"
echo "    lib/logging.py  rjs modifications for configuration"
