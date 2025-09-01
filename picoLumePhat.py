# xLume compatible program for the Pico and ESP32 in MicroPython

from machine import Pin, UART
from neopixel import NeoPixel
from ujson import load, dump
from uasyncio import run, create_task, sleep, Task, sleep_ms
from re import match
from urandom import getrandbits
from math import sin

# Settings
SETTINGS: dict = {
    "ledCount": int,
    "rgb": tuple,
    "effect": int
}

# Current Effect Task
LED_EFFECT_TASK: Task = None

# Pin configuration
LED_STRIP: NeoPixel
SMC_UART = UART(0, baudrate=115200, rx=1)
SENSE_PIN = Pin(2, Pin.IN, Pin.PULL_DOWN)

# Load and save settings
def load_settings():
    global SETTINGS
    with open("settings.json", "r") as f:
        SETTINGS = load(f)

def save_settings():
    with open("settings.json", "w") as f:
        dump(SETTINGS, f)

def update_settings(options: dict):
    global SETTINGS
    global LED_STRIP
    global LED_EFFECT_TASK
    if options["ledCount"] is None and options["rgb"] is None and options["effect"] is None:
        return # Just return, don't even bother saving the file, why the bloody hell would you.
    if options["ledCount"] is not None:
        SETTINGS["ledCount"] = options["ledCount"]
        LED_STRIP = NeoPixel(Pin(0), SETTINGS["ledCount"])
        set_animation(SETTINGS["effect"]) # Restart the animation with the updated LED count.
    if options["rgb"] is not None:
        SETTINGS["rgb"] = options["rgb"]
    if options["effect"] is not None:
        SETTINGS["effect"] = options["effect"]
        set_animation(SETTINGS["effect"])
    save_settings()

def set_animation(effect: int):
    global LED_EFFECT_TASK
    if LED_EFFECT_TASK is not None: # Terminate the current LED effect task
        LED_EFFECT_TASK.cancel()
        LED_EFFECT_TASK: Task = None
    LED_STRIP.fill((0, 0, 0))
    LED_STRIP.write()
    if effect == 0:
        LED_EFFECT_TASK = create_task(static_color())
    elif effect == 1:
        LED_EFFECT_TASK = create_task(gradient())
    elif effect == 2:
        LED_EFFECT_TASK = create_task(static_pulse())
    elif effect == 3:
        LED_EFFECT_TASK = create_task(static_twinkle())
    elif effect == 4:
        LED_EFFECT_TASK = create_task(LEDs_OFF())
    elif effect == 5:
        LED_EFFECT_TASK = create_task(color_wave())
    elif effect == 6:
        LED_EFFECT_TASK = create_task(color_cycle())
    elif effect == 7:
        LED_EFFECT_TASK = create_task(dynamic_pulse())
    elif effect == 8:
        LED_EFFECT_TASK = create_task(dynamic_twinkle())

# Effects
async def static_color():
    LED_STRIP.fill(SETTINGS["rgb"])
    LED_STRIP.write()
async def gradient():
    r1, g1, b1 = SETTINGS["rgb"]
    r2, g2, b2 = 255 - r1, 255 - g1, 255 - b1
    length = SETTINGS["ledCount"]
    for i in range(length):
        factor = i / (length - 1) if length > 1 else 1
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        LED_STRIP[i] = (r, g, b)
    LED_STRIP.write()
async def static_pulse():
    while True:
        for brightness in range(0, 256, 5):
            r = int(SETTINGS["rgb"][0] * brightness / 255)
            g = int(SETTINGS["rgb"][1] * brightness / 255)
            b = int(SETTINGS["rgb"][2] * brightness / 255)
            LED_STRIP.fill((r, g, b))
            LED_STRIP.write()
            await sleep(0.05)
        for brightness in range(255, 0, -5):
            r = int(SETTINGS["rgb"][0] * brightness / 255)
            g = int(SETTINGS["rgb"][1] * brightness / 255)
            b = int(SETTINGS["rgb"][2] * brightness / 255)
            LED_STRIP.fill((r, g, b))
            LED_STRIP.write()
            await sleep(0.05)
async def static_twinkle():
    brightness = [0] * SETTINGS["ledCount"]
    while True:
        # Randomly brighten LEDs
        for i in range(SETTINGS["ledCount"]):
            # Chance to trigger a sparkle or continue fading
            if brightness[i] == 0 and getrandbits(4) == 0:
                brightness[i] = 255  # Full brightness randomly
            elif brightness[i] > 0:
                brightness[i] = max(0, brightness[i] - 15)  # Fade down

            r = int(SETTINGS["rgb"][0] * brightness[i] / 255)
            g = int(SETTINGS["rgb"][1] * brightness[i] / 255)
            b = int(SETTINGS["rgb"][2] * brightness[i] / 255)
            LED_STRIP[i] = (r, g, b)
        LED_STRIP.write()
        await sleep(0.05)
async def LEDs_OFF():
    return
async def color_wave():
    pos = 0
    while True:
        for i in range(SETTINGS["ledCount"]):
            x = (i + pos) * 0.3
            r = int((sin(x) * 127) + 128)  # 0–255
            g = int((sin(x + 2.094) * 127) + 128)  # Offset by 120°
            b = int((sin(x + 4.188) * 127) + 128)  # Offset by 240°
            LED_STRIP[i] = (r, g, b)
        LED_STRIP.write()
        pos += 1
        await sleep(0.05)
async def color_cycle():
    pos = 0
    while True:
        # Calculate RGB values for current cycle position
        r = int((sin(pos * 0.05) * 127) + 128)
        g = int((sin(pos * 0.05 + 2.094) * 127) + 128)
        b = int((sin(pos * 0.05 + 4.188) * 127) + 128)
        # Apply same color to entire strip
        LED_STRIP.fill((r, g, b))
        LED_STRIP.write()
        pos += 1
        await sleep(0.05)
async def dynamic_pulse():
    r, g, b = 255, 0, 0  # Start color
    step = 5
    brightness = 0
    direction = 1  # 1 = brighter, -1 = dimmer
    while True:
        # --- Color Cycle Step ---
        if r == 255 and g < 255 and b == 0:
            g = min(255, g + step)
        elif g == 255 and r > 0 and b == 0:
            r = max(0, r - step)
        elif g == 255 and b < 255 and r == 0:
            b = min(255, b + step)
        elif b == 255 and g > 0 and r == 0:
            g = max(0, g - step)
        elif b == 255 and r < 255 and g == 0:
            r = min(255, r + step)
        elif r == 255 and b > 0 and g == 0:
            b = max(0, b - step)

        # --- Brightness Pulse Step ---
        brightness += direction * 10
        if brightness >= 255:
            brightness = 255
            direction = -1
        elif brightness <= 0:
            brightness = 0
            direction = 1

        # Apply brightness scaling
        r_val = int(r * brightness / 255)
        g_val = int(g * brightness / 255)
        b_val = int(b * brightness / 255)

        # Update LED strip
        LED_STRIP.fill((r_val, g_val, b_val))
        LED_STRIP.write()
        await sleep(0.05)
async def dynamic_twinkle():
    led_count = SETTINGS["ledCount"]
    brightness = [0] * led_count  # Per-LED brightness
    colors = [(0, 0, 0)] * led_count  # Per-LED color

    while True:
        for i in range(led_count):
            if brightness[i] == 0 and getrandbits(4) == 0:
                # Start a twinkle with a random color
                brightness[i] = 255
                colors[i] = (
                    getrandbits(8),  # random R
                    getrandbits(8),  # random G
                    getrandbits(8)   # random B
                )
            elif brightness[i] > 0:
                brightness[i] = max(0, brightness[i] - 15)

            r = int(colors[i][0] * brightness[i] / 255)
            g = int(colors[i][1] * brightness[i] / 255)
            b = int(colors[i][2] * brightness[i] / 255)
            LED_STRIP[i] = (r, g, b)

        LED_STRIP.write()
        await sleep(0.05)
# Helper
def parse_xlume_data(data: str) -> dict:
    parsed_data: dict = {
        "ledCount": None,
        "rgb": None,
        "effect": None
    }
    for line in data.splitlines():
        m = match(r"\[xLume\] - ledCount: (\d+)", line)
        if m:
            parsed_data["ledCount"] = int(m.group(1))
            continue
        # Check for RGB line + next line for Effects
        m = match(r"\[xLume\] - (\d+), (\d+), (\d+)", line)
        if m:
            parsed_data["rgb"] = tuple(map(int, m.groups()))
            continue
        m = match(r"\[xLume\] - Effects: (\d+)", line)
        if m:
            parsed_data["effect"] = int(m.group(1))
    return parsed_data

async def main():
    global LED_STRIP
    global LED_EFFECT_TASK
    load_settings()
    LED_STRIP = NeoPixel(Pin(0), SETTINGS["ledCount"])

    if SENSE_PIN.value() == 1:
        update_settings(SETTINGS)
    
    while True:
        if SENSE_PIN.value() == 1:
            if LED_EFFECT_TASK is None:
                update_settings(SETTINGS)
            if SMC_UART.any():
                await sleep_ms(5) # Wait for final few bits to arrive (somehow fixes a cutoff bug)
                data = SMC_UART.read()
                if data is not None:
                    options = parse_xlume_data(data.decode("utf-8"))
                    update_settings(options)
            await sleep_ms(1)
        if SENSE_PIN.value() == 0:
            if LED_EFFECT_TASK is not None: # Terminate the task
                LED_EFFECT_TASK.cancel()
                LED_EFFECT_TASK: Task = None
            LED_STRIP.fill((0, 0, 0))
            LED_STRIP.write()
            await sleep_ms(1)


run(main())

