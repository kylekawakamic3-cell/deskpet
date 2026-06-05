import board
import busio
import displayio
import time
import os
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# ── Button ────────────────────────────────────────────────────────────────────
import digitalio
from button import GestureButton, EVENT_SHORT, EVENT_LONG

BUTTON_PIN = board.BUTTON   # GPIO0 / onboard BOOT button (change here if using external)
gesture_btn = GestureButton(BUTTON_PIN)

# ── Display Setup ─────────────────────────────────────────────────────────────
displayio.release_displays()
i2c = busio.I2C(board.SCL1, board.SDA1)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3D)
WIDTH, HEIGHT = 128, 64
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# ── Boot Screen: Animated "Connecting..." ─────────────────────────────────────
def show_connecting_screen():
    """Show animated ellipsis while connecting to Wi-Fi."""
    splash = displayio.Group()
    line1 = label.Label(terminalio.FONT, text="Desk Pet", color=0xFFFFFF, x=40, y=22)
    line2 = label.Label(terminalio.FONT, text="Connecting", color=0xFFFFFF, x=22, y=38)
    splash.append(line1)
    splash.append(line2)
    display.root_group = splash

    dots = ["", ".", "..", "..."]
    dot_idx = 0
    last_dot_t = time.monotonic()

    import wifi, ssl, socketpool, adafruit_requests

    ssid     = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    print(f"Connecting to {ssid}...")

    try:
        wifi.radio.connect(ssid, password)
    except Exception as e:
        # Show error and continue without Wi-Fi (offline mode)
        line2.text = "No Wi-Fi"
        display.refresh()
        time.sleep(2)
        print("Wi-Fi failed:", e)
        return None

    # Animate dots until connected
    while not wifi.radio.connected:
        now = time.monotonic()
        if now - last_dot_t >= 0.4:
            dot_idx = (dot_idx + 1) % 4
            line2.text = f"Connecting{dots[dot_idx]}"
            display.refresh()
            last_dot_t = now
        time.sleep(0.05)

    print(f"Connected! IP: {wifi.radio.ipv4_address}")
    line2.text = "Connected!"
    display.refresh()
    time.sleep(0.8)  # brief pause so user sees success

    pool     = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    return requests


# ── Connect to Wi-Fi ──────────────────────────────────────────────────────────
requests = show_connecting_screen()

# ── Import Apps ───────────────────────────────────────────────────────────────
from eyes     import DeskPetApp
from stock    import StockTrackerApp
from fortune  import FortuneApp

# ── Instantiate Apps ──────────────────────────────────────────────────────────
pet_app     = DeskPetApp(WIDTH, HEIGHT)
stock_app   = StockTrackerApp(WIDTH, HEIGHT, symbol="AI", name="C3.AI", requests=requests)
fortune_app = FortuneApp(WIDTH, HEIGHT)

APPS = [pet_app, stock_app, fortune_app]
current_idx = 0

display.root_group = APPS[current_idx].group

print("Ready! Short press = next app | Long press = app action")

# ── Main Loop ─────────────────────────────────────────────────────────────────
while True:
    event = gesture_btn.update()

    if event == EVENT_SHORT:
        # Global: short press always cycles to the next app
        current_idx = (current_idx + 1) % len(APPS)
        display.root_group = APPS[current_idx].group
        print(f"Switched to app {current_idx}: {type(APPS[current_idx]).__name__}")

    elif event == EVENT_LONG:
        # Delegate long press to the active app
        APPS[current_idx].on_button(EVENT_LONG)

    # Tick the active app (animation, timers, API polling)
    APPS[current_idx].update()
