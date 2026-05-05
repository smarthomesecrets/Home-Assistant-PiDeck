#!/usr/bin/env python3
"""
streamdeck_daemon.py
Stream Deck Home Assistant controller for Smart Home Secrets.
Full build guide: https://www.smarthomesecrets.ca/stream-deck-home-assistant-raspberry-pi

SETUP:
1. Fill in config.py with your HA URL and token
2. Replace all YOUR_* placeholders below with your own entity IDs
3. Run: python3 streamdeck_daemon.py
4. Use systemd to run on boot (see README)

PLACEHOLDERS TO REPLACE:
Search for YOUR_ and replace each one with your actual entity ID.
Every placeholder has a comment explaining what it expects.
"""

import time
import threading
import requests
from PIL import Image, ImageDraw, ImageFont
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

from config import HA_URL, HA_TOKEN

# ─── Constants ────────────────────────────────────────────────────────────────

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}

BUTTON_SIZE   = (72, 72)
ICON_SIZE     = (44, 44)
PAGE_LIGHTING = 0
PAGE_CONTROLS = 1

# Path to downloaded Phosphor icon PNGs
# Run download_icons.py to populate this folder
ICON_BASE = "/home/YOUR_USERNAME/streamdeck/icons/png"
# YOUR_USERNAME: the username you created when flashing the Pi OS

current_page = PAGE_LIGHTING

# ─── Colours ──────────────────────────────────────────────────────────────────

WHITE     = (255, 255, 255)
YELLOW    = (255, 210, 50)
RED       = (220, 50, 50)
GREEN     = (50, 200, 80)
BLUE      = (50, 150, 255)
ORANGE    = (255, 140, 0)
CYAN      = (0, 210, 210)
GREY      = (100, 100, 100)
BLACK     = (0, 0, 0)
DIMWHITE  = (160, 160, 160)
DIMYELLOW = (150, 120, 30)
PURPLE    = (160, 80, 220)
PINK      = (220, 100, 180)

# ─── Entity IDs ───────────────────────────────────────────────────────────────
# Replace every YOUR_* value with your actual HA entity ID.
# Find entity IDs in HA: Settings > Devices & Services > [device] > entity

# Lighting — Page 1
# YOUR_OFFICE_LIGHT: Main office ceiling light entity
OFFICE_LIGHT = "YOUR_OFFICE_LIGHT"

# YOUR_FLOOR_LAMP: Floor or uplighter lamp entity
FLOOR_LAMP = "YOUR_FLOOR_LAMP"

# YOUR_DESK_LAMP: Desk lamp entity
DESK_LAMP = "YOUR_DESK_LAMP"

# Govee scene scripts — if your lamps support Govee scenes via HA scripts
# Set to None if you do not have Govee scripts for fire/forest scenes
# YOUR_FLOOR_LAMP_FIRE_SCRIPT: script entity for floor lamp fire scene
#   Example: "govee_scene_floor_lamp_fire"  (script.govee_scene_floor_lamp_fire)
FLOOR_LAMP_FIRE_SCRIPT   = "YOUR_FLOOR_LAMP_FIRE_SCRIPT"
FLOOR_LAMP_FOREST_SCRIPT = "YOUR_FLOOR_LAMP_FOREST_SCRIPT"

# YOUR_DESK_LAMP_FIRE_SCRIPT: script entity for desk lamp fire scene
DESK_LAMP_FIRE_SCRIPT   = "YOUR_DESK_LAMP_FIRE_SCRIPT"
DESK_LAMP_FOREST_SCRIPT = "YOUR_DESK_LAMP_FOREST_SCRIPT"

# DND — requires input_boolean.stream_deck_dnd_active helper in HA
# Create it: Settings > Helpers > Add Helper > Toggle > "Stream Deck DND Active"
DND_BOOLEAN = "input_boolean.stream_deck_dnd_active"

# Locks — Page 2
# YOUR_FRONT_DOOR_LOCK: Front door lock entity
FRONT_DOOR_LOCK = "YOUR_FRONT_DOOR_LOCK"

# YOUR_BACK_DOOR_LOCK: Back or kitchen door lock entity
BACK_DOOR_LOCK = "YOUR_BACK_DOOR_LOCK"

# Media — Page 2
# YOUR_SONOS_ENTITY: Office Sonos or speaker media player entity
OFFICE_SONOS = "YOUR_SONOS_ENTITY"

# YOUR_VOICE_PE_ENTITY: Office Voice PE assist satellite entity
VOICE_PE = "YOUR_VOICE_PE_ENTITY"

# Weather — Page 2
# YOUR_TEMP_SENSOR: Air temperature sensor entity from your weather integration
TEMP_SENSOR = "YOUR_TEMP_SENSOR"

# ─── HA Helpers ───────────────────────────────────────────────────────────────

def ha_get_state(entity_id):
    try:
        r = requests.get(
            f"{HA_URL}/api/states/{entity_id}",
            headers=HEADERS, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def ha_call_service(domain, service, data):
    try:
        requests.post(
            f"{HA_URL}/api/services/{domain}/{service}",
            headers=HEADERS, json=data, timeout=5)
    except Exception:
        pass

def ha_run_script(script_id):
    ha_call_service("script", "turn_on",
                    {"entity_id": f"script.{script_id}"})

# ─── Icon Loading ─────────────────────────────────────────────────────────────

def load_icon(name, weight="light"):
    path = f"{ICON_BASE}/{weight}/{name}.png"
    try:
        img = Image.open(path).convert("RGBA").resize(
            ICON_SIZE, Image.LANCZOS)
        return img
    except Exception:
        return Image.new("RGBA", ICON_SIZE, (0, 0, 0, 0))

def tint_icon(icon_img, colour):
    r, g, b = colour
    tinted = Image.new("RGBA", icon_img.size, (r, g, b, 255))
    tinted.putalpha(icon_img.split()[3])
    return tinted

def make_button(icon_name=None, label=None, top_label=None,
                colour=WHITE, weight="light", bg_color=BLACK,
                text_icon=None, text_icon_colour=WHITE):
    img  = Image.new("RGB", BUTTON_SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    try:
        small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
        tiny  = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
        large = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except Exception:
        small = ImageFont.load_default()
        tiny  = small
        large = small

    cx = BUTTON_SIZE[0] // 2

    if text_icon:
        draw.text((cx, 32), text_icon, fill=text_icon_colour,
                  anchor="mm", font=large)
    elif icon_name:
        icon   = load_icon(icon_name, weight)
        icon   = tint_icon(icon, colour)
        icon_y = 8 if label else 14
        icon_x = (BUTTON_SIZE[0] - ICON_SIZE[0]) // 2
        img.paste(icon, (icon_x, icon_y), mask=icon)

    if top_label:
        draw.text((cx, 5), top_label, fill=GREY, anchor="mm", font=tiny)
    if label:
        draw.text((cx, 65), label, fill=DIMWHITE, anchor="mm", font=small)

    return img

def image_to_native(deck, img):
    return PILHelper.to_native_format(deck, img)

# ─── State Reading ─────────────────────────────────────────────────────────────

def get_office_scene(entity_id):
    state = ha_get_state(entity_id)
    if not state or state["state"] == "off":
        return None
    attrs      = state.get("attributes", {})
    color_mode = attrs.get("color_mode")
    kelvin     = attrs.get("color_temp_kelvin")
    brightness = attrs.get("brightness", 255)
    if color_mode == "color_temp" and kelvin is not None:
        if kelvin >= 4000:
            return "white" if brightness > 180 else "dim_white"
        else:
            return "warm" if brightness > 150 else "dim_warm"
    return "white"

def get_lamp_scene(entity_id):
    state = ha_get_state(entity_id)
    if not state or state["state"] == "off":
        return None
    attrs      = state.get("attributes", {})
    color_mode = attrs.get("color_mode")
    kelvin     = attrs.get("color_temp_kelvin")
    rgb        = attrs.get("rgb_color")
    if color_mode == "color_temp" and kelvin is not None:
        return "white" if kelvin >= 4000 else "warm"
    if color_mode in ("hs", "rgb") and rgb:
        r, g, b = rgb
        if g > r and g > b:
            return "forest"
        if r > g and b < 100:
            return "fire"
        if r > 200 and g > 100:
            return "warm"
    return "white"

def get_dnd_state():
    state = ha_get_state(DND_BOOLEAN)
    return state and state["state"] == "on"

def get_lock_state(entity_id):
    state = ha_get_state(entity_id)
    return state["state"] if state else "unknown"

def get_weather_temp():
    state = ha_get_state(TEMP_SENSOR)
    if state:
        try:
            return f"{float(state['state']):.0f}C"
        except Exception:
            pass
    return "--C"

# ─── Page 1: Lighting ─────────────────────────────────────────────────────────
#
#  Row 0 — Office Light:  [White] [Dim White] [Warm] [Dim Warm] [Off]
#  Row 1 — Floor Lamp:    [White] [Warm] [Fire] [Forest]        [Off Lamps]
#  Row 2 — Desk Lamp:     [White] [Warm] [Fire] [Forest]        [-> Page 2]

def render_page_lighting(deck, office_scene, floor_scene, desk_scene):

    office_buttons = [
        ("white",     "lightbulb",          WHITE,     "White"),
        ("dim_white", "lightbulb",          DIMWHITE,  "Dim White"),
        ("warm",      "lightbulb-filament", YELLOW,    "Warm"),
        ("dim_warm",  "lightbulb-filament", DIMYELLOW, "Dim Warm"),
    ]
    for col, (scene, icon, colour, label) in enumerate(office_buttons):
        active = (office_scene == scene)
        weight = "fill" if active else "light"
        top    = "Office" if col == 0 else None
        img    = make_button(icon, label=label, top_label=top,
                             colour=colour, weight=weight)
        deck.set_key_image(col, image_to_native(deck, img))
    img = make_button("power", label="Off", colour=RED, weight="fill")
    deck.set_key_image(4, image_to_native(deck, img))

    lamp_buttons = [
        ("white",  "lightbulb",          WHITE,  "White"),
        ("warm",   "lightbulb-filament", YELLOW, "Warm"),
        ("fire",   "fire",               RED,    "Fire"),
        ("forest", "tree",               GREEN,  "Forest"),
    ]
    for col, (scene, icon, colour, label) in enumerate(lamp_buttons):
        active = (floor_scene == scene)
        weight = "fill" if active else "light"
        top    = "Floor Lamp" if col == 0 else None
        img    = make_button(icon, label=label, top_label=top,
                             colour=colour, weight=weight)
        deck.set_key_image(5 + col, image_to_native(deck, img))
    img = make_button("power", label="Off Lamps", colour=RED, weight="fill")
    deck.set_key_image(9, image_to_native(deck, img))

    for col, (scene, icon, colour, label) in enumerate(lamp_buttons):
        active = (desk_scene == scene)
        weight = "fill" if active else "light"
        top    = "Desk Lamp" if col == 0 else None
        img    = make_button(icon, label=label, top_label=top,
                             colour=colour, weight=weight)
        deck.set_key_image(10 + col, image_to_native(deck, img))
    img = make_button("arrow-circle-right", label="Controls",
                      colour=CYAN, weight="fill")
    deck.set_key_image(14, image_to_native(deck, img))


# ─── Page 2: Controls ─────────────────────────────────────────────────────────
#
#  Row 1: [DND] [Office TV] [Child 1 Story] [Listen] [Sonos]
#  Row 2: [Package] [GR TV] [Child 2 Story] [Vol-] [Vol+]
#  Row 3: [Weather] [Secure] [Front Lock] [Back Lock] [-> Page 1]
#
# Story button labels: replace "A" and "W" with your children's initials
# Story button colours: replace PINK and BLUE with colours you prefer

def render_page_controls(deck, dnd_on, front_locked, back_locked, temp_str):

    # DND
    if dnd_on:
        img = make_button("bell-slash", label="DND ON",
                          colour=RED, weight="fill")
    else:
        img = make_button("bell", label="DND OFF",
                          colour=DIMWHITE, weight="light")
    deck.set_key_image(0, image_to_native(deck, img))

    # Office TV
    img = make_button("television", label="Office TV",
                      colour=DIMWHITE, weight="light")
    deck.set_key_image(1, image_to_native(deck, img))

    # Child 1 story button
    # "A" = first initial of child 1 — replace with your child's initial
    # PINK = button colour — change to any colour in the colour list above
    # top_label = child's name or nickname shown at top of button
    img = make_button(label="Story", top_label="Child 1",
                      text_icon="A", text_icon_colour=PINK)
    deck.set_key_image(2, image_to_native(deck, img))

    # Listen / Voice PE
    img = make_button("microphone", label="Listen",
                      colour=BLUE, weight="fill")
    deck.set_key_image(3, image_to_native(deck, img))

    # Sonos
    img = make_button("music-notes", label="Sonos",
                      colour=GREEN, weight="fill")
    deck.set_key_image(4, image_to_native(deck, img))

    # Package
    img = make_button("package", label="Package",
                      colour=YELLOW, weight="fill")
    deck.set_key_image(5, image_to_native(deck, img))

    # Great Room TV
    img = make_button("television", label="GR TV",
                      colour=DIMWHITE, weight="light")
    deck.set_key_image(6, image_to_native(deck, img))

    # Child 2 story button
    # "W" = first initial of child 2 — replace with your child's initial
    # BLUE = button colour — change to any colour in the colour list above
    img = make_button(label="Story", top_label="Child 2",
                      text_icon="W", text_icon_colour=BLUE)
    deck.set_key_image(7, image_to_native(deck, img))

    # Vol-
    img = make_button("speaker-low", label="Vol -",
                      colour=DIMWHITE, weight="fill")
    deck.set_key_image(8, image_to_native(deck, img))

    # Vol+
    img = make_button("speaker-high", label="Vol +",
                      colour=DIMWHITE, weight="fill")
    deck.set_key_image(9, image_to_native(deck, img))

    # Weather
    img = make_button("sun", label=temp_str,
                      colour=CYAN, weight="fill")
    deck.set_key_image(10, image_to_native(deck, img))

    # Secure Check
    img = make_button("shield-check", label="Secure",
                      colour=ORANGE, weight="fill")
    deck.set_key_image(11, image_to_native(deck, img))

    # Front Lock
    if front_locked == "locked":
        img = make_button("lock", label="Front",
                          colour=GREEN, weight="fill")
    else:
        img = make_button("lock-open", label="Front",
                          colour=ORANGE, weight="fill")
    deck.set_key_image(12, image_to_native(deck, img))

    # Back Lock
    if back_locked == "locked":
        img = make_button("lock", label="Back",
                          colour=GREEN, weight="fill")
    else:
        img = make_button("lock-open", label="Back",
                          colour=ORANGE, weight="fill")
    deck.set_key_image(13, image_to_native(deck, img))

    # Page nav
    img = make_button("arrow-circle-left", label="Lights",
                      colour=CYAN, weight="fill")
    deck.set_key_image(14, image_to_native(deck, img))

# ─── State Refresh ─────────────────────────────────────────────────────────────

def refresh_display(deck):
    global current_page
    if current_page == PAGE_LIGHTING:
        office_scene = get_office_scene(OFFICE_LIGHT)
        floor_scene  = get_lamp_scene(FLOOR_LAMP)
        desk_scene   = get_lamp_scene(DESK_LAMP)
        render_page_lighting(deck, office_scene, floor_scene, desk_scene)
    else:
        dnd_on     = get_dnd_state()
        front_lock = get_lock_state(FRONT_DOOR_LOCK)
        back_lock  = get_lock_state(BACK_DOOR_LOCK)
        temp_str   = get_weather_temp()
        render_page_controls(deck, dnd_on, front_lock, back_lock, temp_str)

# ─── Button Press Handler ──────────────────────────────────────────────────────

def handle_office_press(col):
    scenes  = ["white", "dim_white", "warm", "dim_warm"]
    scene   = scenes[col]
    current = get_office_scene(OFFICE_LIGHT)
    if current == scene:
        ha_call_service("light", "turn_off", {"entity_id": OFFICE_LIGHT})
        return
    params = {
        "white":     {"brightness_pct": 100, "color_temp_kelvin": 5000},
        "dim_white": {"brightness_pct": 30,  "color_temp_kelvin": 5000},
        "warm":      {"brightness_pct": 100, "color_temp_kelvin": 2700},
        "dim_warm":  {"brightness_pct": 25,  "color_temp_kelvin": 2700},
    }
    ha_call_service("light", "turn_on",
                    {"entity_id": OFFICE_LIGHT, **params[scene]})

def handle_lamp_press(col, entity, script_fire, script_forest):
    scenes  = ["white", "warm", "fire", "forest"]
    scene   = scenes[col]
    current = get_lamp_scene(entity)
    if current == scene:
        ha_call_service("light", "turn_off", {"entity_id": entity})
        return
    if scene == "white":
        ha_call_service("light", "turn_on", {
            "entity_id": entity,
            "brightness_pct": 100,
            "color_temp_kelvin": 5000})
    elif scene == "warm":
        ha_call_service("light", "turn_on", {
            "entity_id": entity,
            "brightness_pct": 80,
            "color_temp_kelvin": 2700})
    elif scene == "fire":
        if script_fire:
            ha_run_script(script_fire)
        else:
            ha_call_service("light", "turn_on", {
                "entity_id": entity,
                "brightness_pct": 100,
                "rgb_color": [255, 80, 0]})
    elif scene == "forest":
        if script_forest:
            ha_run_script(script_forest)
        else:
            ha_call_service("light", "turn_on", {
                "entity_id": entity,
                "brightness_pct": 100,
                "rgb_color": [20, 180, 40]})

def wake_voice_pe():
    ha_call_service("voice_satellite", "wake", {"entity_id": VOICE_PE})

def sonos_smart_play_pause():
    state = ha_get_state(OFFICE_SONOS)
    if not state:
        return
    s = state["state"]
    if s == "playing":
        ha_call_service("media_player", "media_pause",
                        {"entity_id": OFFICE_SONOS})
    elif s == "paused":
        ha_call_service("media_player", "media_play",
                        {"entity_id": OFFICE_SONOS})
    else:
        wake_voice_pe()

def on_key_press(deck, key, state):
    if not state:
        return
    threading.Thread(target=_handle_press,
                     args=(deck, key), daemon=True).start()

def _handle_press(deck, key):
    global current_page

    if current_page == PAGE_LIGHTING:
        row = key // 5
        col = key % 5
        if row == 0 and col < 4:
            handle_office_press(col)
        elif row == 0 and col == 4:
            ha_call_service("light", "turn_off", {"entity_id": OFFICE_LIGHT})
        elif row == 1 and col < 4:
            handle_lamp_press(col, FLOOR_LAMP,
                              FLOOR_LAMP_FIRE_SCRIPT,
                              FLOOR_LAMP_FOREST_SCRIPT)
        elif row == 1 and col == 4:
            ha_call_service("light", "turn_off",
                            {"entity_id": [FLOOR_LAMP, DESK_LAMP]})
        elif row == 2 and col < 4:
            handle_lamp_press(col, DESK_LAMP,
                              DESK_LAMP_FIRE_SCRIPT,
                              DESK_LAMP_FOREST_SCRIPT)
        elif key == 14:
            current_page = PAGE_CONTROLS

    else:
        if key == 0:
            ha_run_script("stream_deck_dnd_toggle")
        elif key == 1:
            ha_run_script("stream_deck_office_tv_play_pause")
        elif key == 2:
            # Child 1 story script ID
            # YOUR_CHILD_1_STORY_SCRIPT: script ID for child 1 story
            # Example: stream_deck_story_child_1
            ha_run_script("YOUR_CHILD_1_STORY_SCRIPT")
        elif key == 3:
            wake_voice_pe()
        elif key == 4:
            sonos_smart_play_pause()
        elif key == 5:
            ha_run_script("stream_deck_package_announce")
        elif key == 6:
            ha_run_script("stream_deck_great_room_tv_play_pause")
        elif key == 7:
            # Child 2 story script ID
            # YOUR_CHILD_2_STORY_SCRIPT: script ID for child 2 story
            # Example: stream_deck_story_child_2
            ha_run_script("YOUR_CHILD_2_STORY_SCRIPT")
        elif key == 8:
            ha_run_script("stream_deck_office_sonos_volume_down")
        elif key == 9:
            ha_run_script("stream_deck_office_sonos_volume_up")
        elif key == 10:
            ha_run_script("stream_deck_weather_announce")
        elif key == 11:
            ha_run_script("stream_deck_secure_check")
        elif key == 12:
            ha_run_script("stream_deck_front_door_lock_toggle")
        elif key == 13:
            ha_run_script("stream_deck_back_door_lock_toggle")
        elif key == 14:
            current_page = PAGE_LIGHTING

    time.sleep(0.3)
    refresh_display(deck)

# ─── Periodic Refresh ─────────────────────────────────────────────────────────

def periodic_refresh(deck, interval=30):
    """Refresh button display every 30 seconds to keep states current."""
    while True:
        time.sleep(interval)
        try:
            refresh_display(deck)
        except Exception:
            pass

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    decks = DeviceManager().enumerate()
    if not decks:
        print("No Stream Deck found. Is it plugged in?")
        print("Check udev rules: /etc/udev/rules.d/99-streamdeck.rules")
        return

    deck = decks[0]
    deck.open()
    deck.reset()
    deck.set_brightness(70)

    print(f"Connected: {deck.deck_type()} with {deck.key_count()} keys")

    deck.set_key_callback(on_key_press)
    refresh_display(deck)

    t = threading.Thread(target=periodic_refresh, args=(deck,), daemon=True)
    t.start()

    print("Stream Deck running. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        deck.reset()
        deck.close()

if __name__ == "__main__":
    main()
