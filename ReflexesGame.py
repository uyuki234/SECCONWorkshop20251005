import board
import busio
import digitalio
import adafruit_ssd1306
import time
import random

# --- Display setup ---
WIDTH = 128
HEIGHT = 64

i2c = busio.I2C(board.GP3, board.GP2)  # SCL=GP3, SDA=GP2
display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def clear_screen():
    display.fill(0)
    display.show()

# --- Buttons (same pinout as your invader game) ---
buttons = {
    "left": digitalio.DigitalInOut(board.GP4),
    "right": digitalio.DigitalInOut(board.GP5),
    "fire": digitalio.DigitalInOut(board.GP6),   # reaction button
    "start": digitalio.DigitalInOut(board.GP7),  # start a round
}
for btn in buttons.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# Helper

def button_pressed(name):
    return not buttons[name].value

# Approximate centered text (6px per char, 8px line height)

def center_text(text, y):
    x = max(0, (WIDTH - len(text) * 6) // 2)
    display.text(text, x, y, 1)

# --- Game states ---
STATE_INTRO = 0
STATE_WAITING = 1
STATE_FLASHED = 2
STATE_RESULT = 3

state = STATE_INTRO
flash_time = 0.0
result_ms = 0

# Random delay range (seconds)
DELAY_MIN = 1.5
DELAY_MAX = 4.0
next_flash_at = 0.0

# Edge detection
prev_fire = False
prev_start = False

# Intro screen
clear_screen()
center_text("Reflexes game", 10)
center_text("START = red", 26)
center_text("Light up,push yerrow!!!", 42)
display.show()

while True:
    # Read buttons
    fire_now = button_pressed("fire")
    start_now = button_pressed("start")

    # --- INTRO: wait for START ---
    if state == STATE_INTRO:
        if start_now and not prev_start:
            clear_screen()
            center_text("black out...", 24)
            display.show()
            # Prepare waiting state
            wait_start = time.monotonic()
            next_flash_at = wait_start + random.uniform(DELAY_MIN, DELAY_MAX)
            state = STATE_WAITING

    # --- WAITING: screen black until random flash ---
    elif state == STATE_WAITING:
        # Early press detection
        if fire_now and not prev_fire:
            clear_screen()
            center_text("FIRE!!", 20)
            center_text("RESTART = red", 36)
            display.show()
            state = STATE_INTRO
        else:
            # Keep screen black
            display.fill(0)
            display.show()
            if time.monotonic() >= next_flash_at:
                # Flash: fill white
                display.fill(1)
                display.show()
                flash_time = time.monotonic()
                state = STATE_FLASHED

    # --- FLASHED: wait for FIRE press and measure time ---
    elif state == STATE_FLASHED:
        if fire_now and not prev_fire:
            press_time = time.monotonic()
            result_ms = int((press_time - flash_time) * 1000)
            # Show result
            display.fill(0)
            center_text("time", 10)
            center_text(f"{result_ms} ms", 28)
            center_text("RESTART = red", 46)
            display.show()
            state = STATE_RESULT

    # --- RESULT: wait for START to go again ---
    elif state == STATE_RESULT:
        if start_now and not prev_start:
            clear_screen()
            center_text("black out...", 24)
            display.show()
            wait_start = time.monotonic()
            next_flash_at = wait_start + random.uniform(DELAY_MIN, DELAY_MAX)
            state = STATE_WAITING

    # Update edges
    prev_fire = fire_now
    prev_start = start_now

    time.sleep(0.01)
