# picoLume
An alternative to the xLume which was designed for the ESP8266 instead this is designed for the Raspberry Pi Pico (and MAYBE the ESP32 if I can be bothered)

How to install: 
1. Make sure you have a Raspberry Pi Pico running MicroPython by getting the latest firmware and copying it over to the pico by holding the BOOTSEL button and plugging the pico in, then dragging and dropping the UF2 file using file explorer.
2. Rename picoLume.py to main.py and copy it AND settings.json to the Pico's onboard flash using something like Thonny IDE
    - DO NOT copy the files over by holding the BOOTSEL button and then dropping them onto the pico, that WILL NOT work!


## Pin explaination:
- 5v - 5V Power to the Pico Zero
- GND - Ground for the Pico
- GPIO 0 - NeoPixel LED strip data line (output)
- GPIO 1 - RX for SMC UART (for reading commands from the xLume app) (input)
- GPIO 2 (Optional) - Disconnected by default, connect to a 1.1-3.3v point on the board IF the pico is on standby power. 
  * NEVER power the LEDs on standby 5v, you can and WILL overload the power supply!!!