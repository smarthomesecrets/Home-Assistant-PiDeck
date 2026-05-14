# Stream Deck Home Assistant — Smart Home Secrets

Physical Home Assistant controls using an Elgato Stream Deck MK2 and a Raspberry Pi 5.
Full build guide at [SmartHomeSecrets.ca](https://www.smarthomesecrets.ca/stream-deck-home-assistant-raspberry-pi).

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-blue.png)](https://www.buymeacoffee.com/smarthomesecrets)


---

## What Is This

A Python daemon running on a headless Pi 5 that connects a Stream Deck MK2 to Home Assistant
over the local REST API. No cloud, no Node-RED, no middleware. 22 controls across two pages
on 15 physical buttons. All scripts and the full daemon are here with placeholder entity IDs
so you can adapt everything to your own setup.

---

## Files In This Repo

### Python Daemon
| File | Purpose |
|---|---|
| `streamdeck_daemon.py` | Main daemon — handles all button rendering, state reading, and HA calls |
| `config.py` | Your HA URL and long-lived access token — fill this in before running |

### HA Scripts (drop into `/config/scripts/` on your HA host)
| File | Purpose |
|---|---|
| `stream_deck_dnd_toggle.yaml` | Sets Z-Wave LED colour on office switches to red (DND on) or white (DND off) |
| `stream_deck_package_announce.yaml` | TTS announcement on porch speaker for package deliveries |
| `stream_deck_wake_office_voice_pe.yaml` | Wakes office Voice PE satellite into active listening mode |
| `stream_deck_weather_announce.yaml` | Weather forecast with pool temp, hot tub temp, swim and hot tub recommendations |
| `stream_deck_secure_check.yaml` | Full security readout on office Sonos plus lights detail to iPhone |
| `stream_deck_office_sonos_smart_play_pause.yaml` | Play/pause Sonos or wake Voice PE if idle |
| `stream_deck_office_sonos_volume_up.yaml` | Office Sonos volume up |
| `stream_deck_office_sonos_volume_down.yaml` | Office Sonos volume down |
| `stream_deck_office_tv_play_pause.yaml` | Office Apple TV play/pause |
| `stream_deck_great_room_tv_play_pause.yaml` | Great Room Apple TV play/pause |
| `stream_deck_front_door_lock_toggle.yaml` | Front door lock toggle |
| `stream_deck_back_door_lock_toggle.yaml` | Kitchen back door lock toggle |
| `stream_deck_story_child_1.yaml` | AI-generated adventure story with daughter as main character, read via Piper |
| `stream_deck_story_child_2.yaml` | AI-generated adventure story with son as main character, read via Piper |

---

## Before You Start

### Required HA Helper
Create this helper in HA before the DND script will work:

- Go to **Settings > Helpers > Add Helper > Toggle**
- Name it: `Stream Deck DND Active`
- Entity ID will be: `input_boolean.stream_deck_dnd_active`

### Check Your Script Directory
Run this on your HA host to confirm where scripts load from:

```bash
grep -i "script" /config/configuration.yaml
```

If you see `script: !include_dir_merge_named scripts`, place all YAML files in `/config/scripts/`.
If you see `script: !include scripts.yaml`, add them to `scripts.yaml` instead.

---

## How to Use the Placeholders

Every entity ID in these files is an `ALL_CAPS_PLACEHOLDER`. Open each file in any text editor,
use Find and Replace to swap placeholders for your own entity IDs, then save.

Each placeholder has a comment above it explaining what it expects and where to find
your equivalent entity in Home Assistant.

**Common placeholders across all scripts:**

| Placeholder | What It Is | Where to Find It |
|---|---|---|
| `YOUR_HA_URL` | Your HA local URL | e.g. `http://192.168.1.x:8123` |
| `YOUR_HA_TOKEN` | Long-lived access token | HA Profile > Long-Lived Access Tokens |
| `YOUR_SONOS_ENTITY` | Office Sonos media player | Settings > Devices > your Sonos |
| `YOUR_PORCH_SONOS_ENTITY` | Porch Sonos media player | Settings > Devices > your porch speaker |
| `YOUR_VOICE_PE_ENTITY` | Office Voice PE assist satellite | Settings > Devices > your Voice PE |
| `YOUR_FRONT_DOOR_LOCK` | Front door lock entity | Settings > Devices > your lock |
| `YOUR_BACK_DOOR_LOCK` | Back door lock entity | Settings > Devices > your lock |
| `YOUR_OFFICE_LIGHT` | Main office ceiling light | Settings > Devices > your light |
| `YOUR_FLOOR_LAMP` | Floor lamp entity | Settings > Devices > your lamp |
| `YOUR_DESK_LAMP` | Desk lamp entity | Settings > Devices > your lamp |
| `YOUR_DND_SWITCH_1` | First Z-Wave switch for DND LED | Settings > Devices > your switch |
| `YOUR_DND_SWITCH_2` | Second Z-Wave switch for DND LED | Settings > Devices > your switch |
| `YOUR_IPHONE_NOTIFY` | iPhone notification service | `notify.mobile_app_YOUR_PHONE_NAME` |
| `YOUR_POOL_TEMP_SENSOR` | Pool water temperature sensor | Settings > Devices > your sensor |
| `YOUR_TUB_TEMP_SENSOR` | Hot tub temperature sensor | Settings > Devices > your sensor |
| `YOUR_CONVERSATION_AGENT` | Claude conversation agent | `conversation.claude_conversation` |
| `YOUR_PERSON_1` | Your HA person entity | Settings > People |
| `YOUR_PERSON_2` | Second person entity | Settings > People |
| `YOUR_PET_SENSOR` | Backyard animal detection sensor | Settings > Devices > your camera |
| `YOUR_BACKYARD_SENSOR` | Backyard person detection sensor | Settings > Devices > your camera |

---

## Testing Before You Connect the Pi

Test every script from HA Developer Tools before wiring anything to a button:

1. Go to **Developer Tools > Services**
2. Search for `script.turn_on`
3. Set `entity_id` to `script.stream_deck_SCRIPT_NAME`
4. Click **Call Service**

If it works in Developer Tools it will work from the Stream Deck.

---

## Running the Daemon

```bash
# Activate the virtual environment
source /home/YOUR_USERNAME/streamdeck-env/bin/activate

# Run manually for testing
python3 /home/YOUR_USERNAME/streamdeck/streamdeck_daemon.py

# Check systemd service status
sudo systemctl status streamdeck

# View live logs
sudo journalctl -u streamdeck -f
```

---

## Dependencies

```bash
pip install streamdeck pillow requests cairosvg
```

Icons use [Phosphor Icons](https://phosphoricons.com) — MIT licensed, downloaded via the
`download_icons.py` script included in the repo.

---

## Questions or Improvements

Drop a comment on the article at SmartHomeSecrets.ca or open an issue here.
If you build your own version with different buttons, share what you came up with.
The Network wants to know.

🔵 [Join the Network at SmartHomeSecrets.ca](https://www.smarthomesecrets.ca)
