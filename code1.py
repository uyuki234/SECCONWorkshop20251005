import board
import busio
import digitalio
import adafruit_ssd1306
import time
import random

# --- Display setup ---
WIDTH = 128
HEIGHT = 64
i2c = busio.I2C(board.GP3, board.GP2)
display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
display.fill(0)
display.show()

# --- Button setup ---
buttons = {
    "left": digitalio.DigitalInOut(board.GP4),
    "right": digitalio.DigitalInOut(board.GP5),
    "fire": digitalio.DigitalInOut(board.GP6),
    "start": digitalio.DigitalInOut(board.GP7)
}
for btn in buttons.values():
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP

# --- Game objects ---
PLAYER_WIDTH = 8
PLAYER_HEIGHT = 4
INVADER_SIZE = 6
BULLET_WIDTH = 2
BULLET_HEIGHT = 4

player_x = WIDTH // 2 - PLAYER_WIDTH // 2
player_y = HEIGHT - PLAYER_HEIGHT - 2
invaders = []
bullets = []

def draw_player():
    display.fill_rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT, 1)

def draw_invaders():
    for inv in invaders:
        display.fill_rect(int(inv["x"]), int(inv["y"]), INVADER_SIZE, INVADER_SIZE, 1)

def draw_bullets():
    for b in bullets:
        display.fill_rect(b["x"], b["y"], BULLET_WIDTH, BULLET_HEIGHT, 1)

def update_bullets():
    global bullets
    for b in bullets:
        b["y"] -= 2
    bullets = [b for b in bullets if b["y"] > 0]

def update_invaders():
    for inv in invaders:
        inv["y"] += 0.25  # 1/4 speed

def check_collisions():
    global invaders, bullets
    new_invaders = []
    for inv in invaders:
        hit = False
        for b in bullets:
            if (b["x"] < inv["x"] + INVADER_SIZE and
                b["x"] + BULLET_WIDTH > inv["x"] and
                b["y"] < inv["y"] + INVADER_SIZE and
                b["y"] + BULLET_HEIGHT > inv["y"]):
                hit = True
                bullets.remove(b)
                break
        if not hit:
            new_invaders.append(inv)
    invaders = new_invaders

def button_pressed(btn):
    return not buttons[btn].value

def show_game_over():
    display.fill(0)
    display.text("GAME OVER", 30, 30, 1)
    display.show()
    while True:
        time.sleep(1)

# --- Main game loop ---
last_invader_time = time.monotonic()
invader_interval = 6.0  # seconds between new rows

while True:
    display.fill(0)

    # Move player
    if button_pressed("left") and player_x > 0:
        player_x -= 2
    if button_pressed("right") and player_x < WIDTH - PLAYER_WIDTH:
        player_x += 2

    # Fire bullet
    if button_pressed("fire"):
        bullets.append({
            "x": player_x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2,
            "y": player_y
        })

    # Generate new invader row
    now = time.monotonic()
    if now - last_invader_time > invader_interval:
        for i in range(0, WIDTH, INVADER_SIZE + 4):
            if random.random() < 0.5:
                invaders.append({"x": i, "y": 0})
        last_invader_time = now

    update_bullets()
    update_invaders()
    check_collisions()

    # Check for game over
    for inv in invaders:
        if inv["y"] + INVADER_SIZE >= HEIGHT:
            show_game_over()

    draw_player()
    draw_invaders()
    draw_bullets()

    display.show()
    time.sleep(0.05)
