#.py.mpy:
#	mpy-cross -o $@ $< 

# specify port for micropython instance (using mpremote shortcut)
#   MP_PORT=         empty if default (first one mpremote finds)
#           a0       ttyACM0, ..
#           a1                ..
#set with `make MP_PORT=a0`
MP_PORT=

# mcu:  options are samd, rp2, esp32c3, nrf
MP_MCU=esp32c3
DO_START=0
STARTMODULE=main.holiday.py

MAIN = startholiday.py
EFFECTS = effects.py boom.py fwpartx.py effect_panel.py fire.py simpfirefly.py twinkle.py randBlinkerFade.py lightning.py
LEDSEQ = everyday.py holiday.py runleds.py cpixels.py halloween.py
PYMODULE = colorsupport.py checkstart.py mqttquick.py netconnect.py webrepl_cfg.py 
CFIGMODULE = config.$(MP_MCU).py

#esp32c3,s3 used but (probably) builtins
# ds18x20 neopixel ntptime umqtt.simple time
# micropython_lib: time adds strftime to time module
STDEXTLIB = neopixel ntptime umqtt.simple ds18x20 time
CPYEXTLIB = fixlib/logging.mpy

%.mpy: lib/%.py
	mpy-cross -o $@ $<

fixlib/logging.mpy: fixlib/rjs.logging.py
	mpy-cross -o $@ $<

%.mpy: %.py
	mpy-cross -o $@ $<

# uses mpremote cp, which will overwrite files if they exist on mcu
upload: $(MAIN) $(LEDSEQ) $(PYMODULE) $(CFIGMODULE)
	mpremote $(MP_PORT) cp $(MAIN) :
	# assumes existence of :/lib/ on mcu
	mpremote $(MP_PORT) cp $(LEDSEQ) :
	mpremote $(MP_PORT) cp $(PYMODULE) :
	mpremote $(MP_PORT) cp $(EFFECTS) :
	mpremote $(MP_PORT) cp $(CFIGMODULE) :config.py
ifneq "$(STARTMODULE)" ""
	mpremote $(MP_PORT) cp $(STARTMODULE) :main.py
endif
ifneq  "$(DO_START)" "1"
	mpremote $(MP_PORT) cp nostart :nostart
endif

extlibs:
	mpremote mip install $(STDEXTLIB)
	mpremote cp $(CPYEXTLIB) :/lib


help:
	@echo "Holiday pixel source load"
	@echo "upload:  default target, load python files to mcu"
	@echo "         MP_PORT port to use default $(MP_PORT)"
	@echo "         MP_MCU mcu to use (rp2, esp32c3, esp32s3) default $(MP_MCU)"
	@echo "         DO_START=1 if auto start of startholiday"
