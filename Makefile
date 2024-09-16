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

MAIN = startholiday.py
LEDSEQ = everyday.py holiday.py runleds.py twinkle.py cbytes.py
PYMODULE = colorsupport.py mqttquick.py netconnect.py webrepl_cfg.py
CFIGMODULE = config.$(MP_MCU).py

%.mpy: libs/%.py
	mpy-cross -o $@ $<

%.mpy: %.py
	mpy-cross -o $@ $<

# uses mpremote cp, which will overwrite files if they exist on mcu
upload: $(MAIN) $(LEDSEQ) $(PYMODULE) $(CFIGMODULE) $(STARTMODULE)
	mpremote $(MP_PORT) cp $(MAIN) :
	# assumes existence of :/lib/ on mcu
	mpremote $(MP_PORT) cp $(MAIN) :
	mpremote $(MP_PORT) cp $(LEDSEQ) :
	mpremote $(MP_PORT) cp $(PYMODULE) :
	mpremote $(MP_PORT) cp $(CFIGMODULE) :config.py
ifneq "$(STARTMODULE)" ""
	mpremote $(MP_PORT) cp $(STARTMODULE) :main.py
endif

#config.py:
#	python buildconfig.py $(MP_MCU)

help:
	@echo "Holiday pixel source load"
	@echo "upload:  default target, load python files to mcu"
	@echo "         STARTMODULE is empty or main.py $(STARTMODULE)"
	@echo "         MP_PORT port to use default $(MP_PORT)"
	@echo "         MP_MCU mcu to use (rp2, esp32c3) default $(MP_MCU)"
