# picoLume
An alternative to the xLume which was designed for the ESP8266 instead this is designed for the Raspberry Pi Pico (and MAYBE the ESP32 if I can be bothered)

As of now there are two different versions because I can't find a 5v power point on the phat that isnt standby where I want to install my pico, however I might have an idea what to do.

How to install: 
1. Make sure you have a Raspberry Pi Pico running MicroPython by getting the latest firmware and copying it over to the pico by holding the BOOTSEL button and plugging the pico in, then dragging and dropping the UF2 file using file explorer.
2. Rename picoLume.py to main.py and copy it AND settings.json to the Pico's onboard flash using something like Thonny IDE
    - DO NOT copy the files over by holding the BOOTSEL button and then dropping them onto the pico, that WILL NOT work!


## Pin explaination:
- 5v - 5V Power to the Pico Zero
- GND - Ground for the Pico
- GPIO 0 - NeoPixel LED strip data line (output)
- GPIO 1 - RX for SMC UART (for reading commands from the xLume app) (input)
- GPIO 2 (Optional) - Power sense wire (input)
    - This pin needs to be connected to a 1-3v point on the Xbox 360 board which isn't standby voltage only IF the Pico is using standby 5v (mainly on phats) due to there not being an easy 5v point on phats to use for the pico that aren't standby. When this pin is connected the pico will shut the leds off when the console is off, and turn them on when the console is on
    (NOTE: If this pin is disconnected (for something like a slim), it will be pulled high turning the LEDs on when the pico is turned on, HOWEVER, you can still use it on a slim if you want to.)