#!/usr/bin/env python3
"""
Downloads the full Phosphor Icons set (all 6 weights) as SVGs from jsDelivr,
then converts every SVG to a 72x72 PNG ready for use with the Stream Deck.

Output structure:
  /home/pideck/streamdeck/icons/svg/<weight>/<name>-<weight>.svg
  /home/pideck/streamdeck/icons/png/<weight>/<name>.png

Usage:
  python3 download_icons.py

Takes 5-15 minutes depending on connection speed (1,248 icons x 6 weights).
"""

import os
import time
import urllib.request
import urllib.error

# ─── Config ──────────────────────────────────────────────────────────────────

VERSION    = "2.1.1"
BASE_URL   = f"https://cdn.jsdelivr.net/npm/@phosphor-icons/core@{VERSION}/assets"
BASE_DIR   = "/home/pideck/streamdeck/icons"
SVG_DIR    = os.path.join(BASE_DIR, "svg")
PNG_DIR    = os.path.join(BASE_DIR, "png")
WEIGHTS    = ["regular", "thin", "light", "bold", "fill", "duotone"]
PNG_SIZE   = 72  # Stream Deck MK2 button resolution

# Full icon list — 1,248 icons as of Phosphor 2.1.1
ICONS = [
    "address-book","air-traffic-control","airplane","airplane-in-flight",
    "airplane-landing","airplane-takeoff","airplane-tilt","airplay",
    "alarm","alien","align-bottom","align-bottom-simple","align-center-horizontal",
    "align-center-horizontal-simple","align-center-vertical",
    "align-center-vertical-simple","align-left","align-left-simple",
    "align-right","align-right-simple","align-top","align-top-simple",
    "anchor","anchor-simple","android-logo","angle","angular-logo","aperture",
    "app-store-logo","app-window","apple-logo","apple-podcasts-logo","archive",
    "archive-box","archive-tray","armchair","arrow-arc-left","arrow-arc-right",
    "arrow-bend-double-up-left","arrow-bend-double-up-right","arrow-bend-down-left",
    "arrow-bend-down-right","arrow-bend-left-down","arrow-bend-left-up",
    "arrow-bend-right-down","arrow-bend-right-up","arrow-bend-up-left",
    "arrow-bend-up-right","arrow-circle-down","arrow-circle-down-left",
    "arrow-circle-down-right","arrow-circle-left","arrow-circle-right",
    "arrow-circle-up","arrow-circle-up-left","arrow-circle-up-right",
    "arrow-clockwise","arrow-counter-clockwise","arrow-down","arrow-down-left",
    "arrow-down-right","arrow-elbow-down-left","arrow-elbow-down-right",
    "arrow-elbow-left","arrow-elbow-left-down","arrow-elbow-left-up",
    "arrow-elbow-right","arrow-elbow-right-down","arrow-elbow-right-up",
    "arrow-elbow-up-left","arrow-elbow-up-right","arrow-fat-down",
    "arrow-fat-left","arrow-fat-line-down","arrow-fat-line-left",
    "arrow-fat-line-right","arrow-fat-line-up","arrow-fat-lines-down",
    "arrow-fat-lines-left","arrow-fat-lines-right","arrow-fat-lines-up",
    "arrow-fat-right","arrow-fat-up","arrow-left","arrow-line-down",
    "arrow-line-down-left","arrow-line-down-right","arrow-line-left",
    "arrow-line-right","arrow-line-up","arrow-line-up-left","arrow-line-up-right",
    "arrow-right","arrow-square-down","arrow-square-down-left",
    "arrow-square-down-right","arrow-square-in","arrow-square-left",
    "arrow-square-out","arrow-square-right","arrow-square-up","arrow-square-up-left",
    "arrow-square-up-right","arrow-u-down-left","arrow-u-down-right",
    "arrow-u-left-down","arrow-u-left-up","arrow-u-right-down","arrow-u-right-up",
    "arrow-u-up-left","arrow-u-up-right","arrow-up","arrow-up-left",
    "arrow-up-right","arrows-clockwise","arrows-counter-clockwise","arrows-down-up",
    "arrows-horizontal","arrows-in","arrows-in-cardinal","arrows-in-line-horizontal",
    "arrows-in-line-vertical","arrows-in-simple","arrows-left-right",
    "arrows-merge","arrows-out","arrows-out-cardinal","arrows-out-line-horizontal",
    "arrows-out-line-vertical","arrows-out-simple","arrows-split",
    "arrows-vertical","article","article-medium","article-ny-times","asterisk",
    "at","atom","avocado","axe","baby","baby-carriage","backpack","backspace",
    "bag","bag-simple","balloon","bandaids","bank","barbell","barcode",
    "barn","barricade","baseball","baseball-cap","baseball-helmet","basket",
    "basketball","bathtub","battery-charging","battery-charging-vertical",
    "battery-empty","battery-full","battery-high","battery-low","battery-medium",
    "battery-plus","battery-plus-vertical","battery-vertical-empty",
    "battery-vertical-full","battery-vertical-high","battery-vertical-low",
    "battery-vertical-medium","battery-warning","battery-warning-vertical",
    "bed","beer-bottle","beer-stein","behance-logo","bell","bell-ringing",
    "bell-simple","bell-simple-ringing","bell-simple-slash","bell-simple-z",
    "bell-slash","bell-z","bezier-curve","bicycle","binoculars","biohazard",
    "bird","blueprint","bluetooth","bluetooth-connected","bluetooth-slash",
    "bluetooth-x","boat","bomb","bone","book","book-bookmark","book-open",
    "book-open-text","bookmark","bookmark-simple","bookmarks","bookmarks-simple",
    "books","boot","bounding-box","brackets-angle","brackets-curly",
    "brackets-round","brackets-square","brain","brandy","bread","bridge",
    "briefcase","briefcase-metal","broadcast","broom","browser","browsers",
    "bug","bug-beetle","bug-droid","buildings","bus","butterfly","cable-car",
    "cactus","cake","calculator","calendar","calendar-blank","calendar-check",
    "calendar-dot","calendar-dots","calendar-heart","calendar-minus",
    "calendar-plus","calendar-slash","calendar-star","calendar-x",
    "call-bell","camera","camera-plus","camera-rotate","camera-slash",
    "camera-viewfinder","campfire","car","car-battery","car-profile",
    "car-simple","cardholder","cards","caret-circle-double-down",
    "caret-circle-double-left","caret-circle-double-right","caret-circle-double-up",
    "caret-circle-down","caret-circle-left","caret-circle-right",
    "caret-circle-up","caret-double-down","caret-double-left",
    "caret-double-right","caret-double-up","caret-down","caret-left",
    "caret-right","caret-up","carrot","cassette-tape","castle","cat",
    "cell-signal-full","cell-signal-high","cell-signal-low","cell-signal-medium",
    "cell-signal-none","cell-signal-slash","cell-signal-x","certificate",
    "chair","chalkboard","chalkboard-simple","chalkboard-teacher","champagne",
    "charging-station","chart-bar","chart-bar-horizontal","chart-donut",
    "chart-line","chart-line-down","chart-line-up","chart-pie","chart-pie-slice",
    "chart-polar","chart-scatter","chat","chat-centered","chat-centered-dots",
    "chat-centered-text","chat-circle","chat-circle-dots","chat-circle-slash",
    "chat-circle-text","chat-dots","chat-slash","chat-teardrop",
    "chat-teardrop-dots","chat-teardrop-text","chat-text","check","check-circle",
    "check-fat","check-square","check-square-offset","checks","church",
    "cigarette","cigarette-slash","circle","circle-dashed","circle-half",
    "circle-half-tilt","circle-notch","circles-four","circles-three",
    "circles-three-plus","circuitry","city","clipboard","clipboard-text",
    "clock","clock-afternoon","clock-clockwise","clock-counter-clockwise",
    "clock-countdown","clock-user","closed-captioning","cloud","cloud-arrow-down",
    "cloud-arrow-up","cloud-check","cloud-fog","cloud-lightning","cloud-moon",
    "cloud-rain","cloud-slash","cloud-snow","cloud-sun","cloud-warning","club",
    "coat-hanger","cobalt-session-logo","code","code-block","code-simple",
    "codepen-logo","codesandbox-logo","coffee","coin","coin-vertical","coins",
    "columns","command","compass","compass-rose","compass-tool","computer-tower",
    "confetti","contactless-payment","control-knobs","cookie","cooking-pot",
    "copy","copy-simple","copyleft","copyright","couch","cpu","credit-card",
    "crop","cross","crosshair","crosshair-simple","crown","crown-simple",
    "cube","cube-focus","cube-transparent","currency-btc","currency-circle-dollar",
    "currency-cny","currency-dollar","currency-dollar-simple","currency-eth",
    "currency-eur","currency-gbp","currency-inr","currency-jpy","currency-krw",
    "currency-kzt","currency-ngn","currency-rub","cursor","cursor-click",
    "cursor-text","cylinder","database","desktop","desktop-tower","detective",
    "device-mobile","device-mobile-camera","device-mobile-slash",
    "device-mobile-speaker","device-rotate","device-tablet","device-tablet-camera",
    "device-tablet-speaker","devices","diamond","diamond-four","diamonds-four",
    "dice-five","dice-four","dice-one","dice-six","dice-three","dice-two",
    "disc","discord-logo","divide","dna","dog","door","door-open","dot",
    "dots-nine","dots-six","dots-six-vertical","dots-three","dots-three-circle",
    "dots-three-circle-vertical","dots-three-outline","dots-three-outline-vertical",
    "dots-three-vertical","download","download-simple","dresser","drone",
    "drop","drop-half","drop-half-bottom","drop-simple","drop-slash",
    "dropbox-logo","ear","ear-slash","egg","egg-crack","eject","elevator",
    "empty","engine","envelope","envelope-open","envelope-simple",
    "envelope-simple-open","equalizer","eraser","escalator-down","escalator-up",
    "exam","exclamation-mark","export","eye","eye-closed","eye-slash",
    "eyedropper","eyedropper-sample","eyeglasses","face-mask","factory",
    "faders","faders-horizontal","fan","fast-forward","fast-forward-circle",
    "feather","figma-logo","file","file-archive","file-arrow-down",
    "file-arrow-up","file-audio","file-cloud","file-code","file-css",
    "file-csv","file-dashed","file-doc","file-dotted","file-html","file-image",
    "file-jpg","file-js","file-jsx","file-lock","file-magnifying-glass",
    "file-minus","file-pdf","file-plus","file-png","file-ppt","file-py",
    "file-rs","file-search","file-sql","file-svg","file-text","file-ts",
    "file-tsx","file-txt","file-video","file-vue","file-x","file-xls",
    "file-zip","files","film-reel","film-script","film-slate","film-strip",
    "fingerprint","fingerprint-simple","fire","fire-extinguisher","fire-simple",
    "first-aid","first-aid-kit","fish","fish-simple","flag","flag-banner",
    "flag-banner-fold","flag-checkered","flag-pennant","flame","flashlight",
    "flask","floppy-disk","floppy-disk-back","flow-arrow","flower","flower-lotus",
    "flower-tulip","folder","folder-dashed","folder-dotted","folder-lock",
    "folder-minus","folder-notch","folder-notch-minus","folder-notch-open",
    "folder-notch-plus","folder-open","folder-plus","folder-simple",
    "folder-simple-dashed","folder-simple-dotted","folder-simple-lock",
    "folder-simple-minus","folder-simple-plus","folder-simple-star",
    "folder-simple-user","folder-star","folder-user","folders","football",
    "football-helmet","footprints","fork-knife","frame-corners","framer-logo",
    "function","funnel","funnel-simple","funnel-simple-x","funnel-x",
    "game-controller","garage","gas-can","gas-pump","gauge","gear",
    "gear-fine","gear-six","gender-female","gender-intersex","gender-male",
    "gender-neuter","gender-nonbinary","gender-transgender","ghost",
    "gif","gift","git-branch","git-commit","git-diff","git-fork","git-merge",
    "git-pull-request","github-logo","gitlab-logo","gitlab-logo-simple",
    "globe","globe-hemisphere-east","globe-hemisphere-west","globe-simple",
    "globe-simple-x","globe-stand","globe-x","goggles","golf","goodreads-logo",
    "google-cardboard-logo","google-chrome-logo","google-drive-logo",
    "google-logo","google-photos-logo","google-play-logo","google-podcasts-logo",
    "grab","graduation-cap","grains","grains-slash","graph","grid-four",
    "grid-nine","guitar","hamburger","hammer","hand","hand-arrow-down",
    "hand-arrow-up","hand-coins","hand-deposit","hand-eye","hand-fist",
    "hand-grabbing","hand-heart","hand-palm","hand-peace","hand-pointing",
    "hand-soap","hand-swipe-left","hand-swipe-right","hand-tap",
    "hand-waving","hand-withdraw","handbag","handbag-simple","hands-clapping",
    "hands-praying","handshake","hard-drive","hard-drives","hash",
    "head-circuit","headlights","headphones","headset","heart","heart-break",
    "heart-half","heart-straight","heart-straight-break","heartbeat",
    "hexagon","high-heel","highlighter","highlighter-circle","hockey",
    "hoodie","horse","hourglass","hourglass-high","hourglass-low",
    "hourglass-medium","house","house-line","house-simple","hurricane",
    "ice-cream","identification-badge","identification-card","image",
    "image-broken","image-square","images","images-square","infinity",
    "info","instagram-logo","intersect","intersect-square","intersect-three",
    "island","jar","jar-label","jeep","joystick","kanban","key","key-return",
    "keyboard","keyhole","knife","ladder","lamp","laptop","lasso","layout",
    "leaf","lego","lego-smiley","less-than","less-than-or-equal","letter-circle-h",
    "letter-circle-p","letter-circle-v","lifebuoy","lightbulb","lightbulb-filament",
    "lighter","lightning","lightning-a","lightning-slash","line-segment",
    "line-segments","link","link-break","link-simple","link-simple-break",
    "link-simple-horizontal","link-simple-horizontal-break","linkedin-logo",
    "linux-logo","list","list-bullets","list-checks","list-dashes","list-heart",
    "list-magnifying-glass","list-numbers","list-plus","list-star","lock",
    "lock-key","lock-key-open","lock-laminated","lock-laminated-open",
    "lock-open","lock-simple","lock-simple-open","lockers","log","magic-wand",
    "magnet","magnet-straight","magnifying-glass","magnifying-glass-minus",
    "magnifying-glass-plus","map-pin","map-pin-area","map-pin-line",
    "map-pin-plus","map-pin-simple","map-pin-simple-area","map-pin-simple-line",
    "map-trifold","markdown-logo","marker","marker-circle","martini",
    "mask-happy","mask-sad","math-operations","medal","medal-military",
    "medium-logo","megaphone","megaphone-simple","member-of","memory",
    "messenger-logo","meta-logo","meteor","metronome","microphone",
    "microphone-slash","microphone-stage","microscope","microsoft-excel-logo",
    "microsoft-outlook-logo","microsoft-teams-logo","microsoft-word-logo",
    "minus","minus-circle","minus-square","money","monitor","monitor-arrow-up",
    "monitor-play","moon","moon-stars","moped","mophead","mosque","motorcycle",
    "mountains","mouse","mouse-left-click","mouse-middle-click","mouse-right-click",
    "mouse-scroll","mouse-simple","music-note","music-note-simple","music-notes",
    "music-notes-minus","music-notes-plus","music-notes-simple","navigation-arrow",
    "needle","newspaper","newspaper-clipping","note","note-blank","note-pencil",
    "notebook","notebook-text","notepad","notepad-text","number-circle-eight",
    "number-circle-five","number-circle-four","number-circle-nine",
    "number-circle-one","number-circle-seven","number-circle-six",
    "number-circle-three","number-circle-two","number-circle-zero",
    "number-eight","number-five","number-four","number-nine","number-one",
    "number-seven","number-six","number-square-eight","number-square-five",
    "number-square-four","number-square-nine","number-square-one",
    "number-square-seven","number-square-six","number-square-three",
    "number-square-two","number-square-zero","number-three","number-two",
    "number-zero","nut","ny-times-logo","octagon","office-chair","onigiri",
    "open-ai-logo","option","orange-slice","oven","package","paint-brush",
    "paint-brush-broad","paint-brush-household","paint-bucket","paint-roller",
    "palette","pants","paper-plane","paper-plane-right","paper-plane-tilt",
    "paperclip","paperclip-horizontal","parachute","paragraph","parallelogram",
    "park","password","path","pause","pause-circle","paw-print","peace",
    "pen","pen-nib","pen-nib-straight","pencil","pencil-circle","pencil-line",
    "pencil-ruler","pencil-simple","pencil-simple-line","pencil-simple-slash",
    "pencil-slash","pentagon","percent","person","person-arms-spread",
    "person-simple","person-simple-bike","person-simple-hike","person-simple-run",
    "person-simple-ski","person-simple-ski-jump","person-simple-ski-jumping",
    "person-simple-snowboard","person-simple-swim","person-simple-tai-chi",
    "person-simple-throw","person-simple-walk","perspective","phone",
    "phone-call","phone-disconnect","phone-incoming","phone-list",
    "phone-outgoing","phone-pause","phone-plus","phone-slash","phone-transfer",
    "phone-x","phosphor-logo","pi","piano-keys","picture-in-picture",
    "piggy-bank","pill","ping-pong","pinterest-logo","pinwheel","pipe",
    "pipe-wrench","pizza","placeholder","planet","plant","play","play-circle",
    "play-pause","playlist","plug","plug-charging","plugs","plugs-connected",
    "plus","plus-circle","plus-minus","plus-square","poker-chip","police-car",
    "polygon","popcorn","popsicle","potted-plant","power","prescription",
    "presentation","presentation-chart","printer","prohibit","prohibit-inset",
    "projector-screen","projector-screen-chart","pulse","push-pin",
    "push-pin-simple","push-pin-simple-slash","push-pin-slash","puzzle-piece",
    "puzzle-piece-simple","qr-code","question","question-mark","queue",
    "quotes","radical","radio","radio-button","radioactive","rainbow",
    "read-cv-logo","receipt","receipt-x","record","rectangle","recycle",
    "reddit-logo","repeat","repeat-once","resize","rewind","rewind-circle",
    "road-horizon","robot","rocket","rocket-launch","rows","rows-plus-bottom",
    "rows-plus-top","rss","rss-simple","rug","ruler","scales","scan","scissors",
    "scooter","screencast","seal","seal-check","seal-percent","seal-question",
    "seal-warning","seat","seatbelt","security-camera","selection",
    "selection-all","selection-background","selection-foreground",
    "selection-inverse","selection-minus","selection-plus","selection-slash",
    "share","share-fat","share-network","shield","shield-check","shield-checkered",
    "shield-chevron","shield-plus","shield-slash","shield-star","shield-warning",
    "shirt","shooting-star","shopping-bag","shopping-bag-open","shopping-cart",
    "shopping-cart-simple","shovel","shower","shuffle","shuffle-angular",
    "shuffle-simple","sidebar","sidebar-simple","sign-in","sign-out","signal-high",
    "signal-low","signal-medium","signal-none","signal-slash","signal-wifi-bad",
    "signal-wifi-connected-1","signal-wifi-connected-2","signal-wifi-connected-3",
    "signal-wifi-high","signal-wifi-low","signal-wifi-medium","signal-wifi-none",
    "signal-wifi-slash","signal-wifi-x","signature","signpost","sim-card",
    "siren","sketch-logo","skip-back","skip-back-circle","skip-forward",
    "skip-forward-circle","skull","sliders","sliders-horizontal","smiley",
    "smiley-angry","smiley-blank","smiley-meh","smiley-melting","smiley-nervous",
    "smiley-sad","smiley-sticker","smiley-wink","smiley-x-eyes","sneaker",
    "sneaker-move","snowflake","soccer-ball","sort-ascending","sort-descending",
    "soundcloud-logo","spade","sparkle","speaker-hifi","speaker-high",
    "speaker-low","speaker-none","speaker-simple-high","speaker-simple-low",
    "speaker-simple-none","speaker-simple-slash","speaker-simple-x",
    "speaker-slash","speaker-x","spinner","spinner-ball","spinner-gap",
    "spiral","split-horizontal","split-vertical","spotify-logo","square",
    "square-half","square-half-bottom","square-logo","stack","stack-minus",
    "stack-overflow-logo","stack-plus","stack-simple","stairs","stamp",
    "standard-definition","star","star-and-crescent","star-four","star-half",
    "star-of-david","star-of-life","steering-wheel","steps","stethoscope",
    "sticker","stop","stop-circle","storefront","strategy","stripe-logo",
    "student","sub-set-of","sub-set-proper-of","subtitles","subtitles-slash",
    "subtract-square","suitcase","suitcase-rolling","suitcase-simple","sun",
    "sun-dim","sun-horizon","sunglasses","super-set-of","super-set-proper-of",
    "swap","swatches","swimming-pool","sword","synagogue","syringe","table",
    "tabs","tag","tag-chevron","tag-simple","target","taxi","tea-bag","telegram-logo",
    "television","television-simple","tennis-ball","tent","terminal","terminal-window",
    "test-tube","text-a-underline","text-aa","text-align-center","text-align-justify",
    "text-align-left","text-align-right","text-b","text-columns","text-h",
    "text-h-five","text-h-four","text-h-one","text-h-six","text-h-three",
    "text-h-two","text-indent","text-italic","text-outdent","text-strikethrough",
    "text-subscript","text-superscript","text-t","text-t-slash","text-underline",
    "textbox","thermometer","thermometer-cold","thermometer-hot",
    "thermometer-simple","thumbs-down","thumbs-up","ticket","tidal-logo",
    "timer","toggle-left","toggle-right","toilet","toilet-paper","toolbox",
    "tooth","tornado","tote","tote-simple","trademark","traffic-cone",
    "traffic-sign","traffic-signal","train","train-regional","train-simple",
    "train-tram","translate","trash","trash-simple","tray","tray-arrow-down",
    "tray-arrow-up","tree","tree-evergreen","tree-palm","tree-structure",
    "trend-down","trend-up","triangle","triangle-dashed","trophy","truck",
    "truck-trailer","tumblr-logo","twitch-logo","twitter-logo","umbrella",
    "umbrella-simple","union","unite","unite-square","upload","upload-simple",
    "usb","user","user-check","user-circle","user-circle-check",
    "user-circle-dashed","user-circle-gear","user-circle-minus","user-circle-plus",
    "user-focus","user-gear","user-list","user-minus","user-plus","user-rectangle",
    "user-sound","user-square","user-switch","users","users-four","users-three",
    "vault","vibrate","video","video-camera","video-camera-slash","video-conference",
    "vignette","visor","voicemail","volleyball","wall","wallet","warehouse",
    "warning","warning-circle","warning-diamond","warning-octagon","watch",
    "waves","webcam","webcam-slash","whatsapp-logo","wheelchair","wheelchair-motion",
    "wifi-high","wifi-low","wifi-medium","wifi-none","wifi-slash","wifi-x",
    "wind","windows-logo","wine","wrench","x","x-circle","x-logo","x-square",
    "yarn","yin-yang","youtube-logo",
]

def download_svgs():
    """Download all SVG files from jsDelivr CDN."""
    total   = len(ICONS) * len(WEIGHTS)
    done    = 0
    errors  = []

    for weight in WEIGHTS:
        out_dir = os.path.join(SVG_DIR, weight)
        os.makedirs(out_dir, exist_ok=True)

        for icon in ICONS:
            filename = f"{icon}-{weight}.svg"
            url      = f"{BASE_URL}/{weight}/{filename}"
            out_path = os.path.join(out_dir, filename)

            if os.path.exists(out_path):
                done += 1
                continue

            for attempt in range(3):
                try:
                    urllib.request.urlretrieve(url, out_path)
                    done += 1
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # Icon doesn't exist in this weight — skip silently
                        done += 1
                        break
                    time.sleep(1)
                except Exception:
                    time.sleep(2)
            else:
                errors.append(f"{weight}/{icon}")

            if done % 100 == 0:
                print(f"  Downloaded {done}/{total}...")

    return errors

def convert_to_png():
    """Convert all downloaded SVGs to 72x72 PNGs using cairosvg."""
    try:
        import cairosvg
    except ImportError:
        print("cairosvg not installed — skipping PNG conversion.")
        print("Run: pip install cairosvg")
        return

    total = 0
    done  = 0

    for weight in WEIGHTS:
        svg_weight_dir = os.path.join(SVG_DIR, weight)
        png_weight_dir = os.path.join(PNG_DIR, weight)
        os.makedirs(png_weight_dir, exist_ok=True)

        svgs = [f for f in os.listdir(svg_weight_dir) if f.endswith(".svg")]
        total += len(svgs)

        for svg_file in svgs:
            icon_name = svg_file.replace(f"-{weight}.svg", "")
            svg_path  = os.path.join(svg_weight_dir, svg_file)
            png_path  = os.path.join(png_weight_dir, f"{icon_name}.png")

            if os.path.exists(png_path):
                done += 1
                continue

            try:
                cairosvg.svg2png(
                    url=svg_path,
                    write_to=png_path,
                    output_width=PNG_SIZE,
                    output_height=PNG_SIZE,
                )
                done += 1
            except Exception as e:
                print(f"  Failed to convert {svg_file}: {e}")

            if done % 200 == 0:
                print(f"  Converted {done}/{total}...")

    print(f"  Converted {done}/{total} SVGs to PNG.")

def main():
    os.makedirs(SVG_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)

    print(f"Downloading {len(ICONS)} icons x {len(WEIGHTS)} weights from jsDelivr...")
    print(f"SVG output: {SVG_DIR}")
    errors = download_svgs()

    if errors:
        print(f"\nFailed to download {len(errors)} icons:")
        for e in errors:
            print(f"  {e}")
    else:
        print("All SVGs downloaded successfully.")

    print(f"\nConverting SVGs to {PNG_SIZE}x{PNG_SIZE} PNGs...")
    print(f"PNG output: {PNG_DIR}")
    convert_to_png()

    print("\nDone. Icon set ready at:")
    print(f"  SVGs: {SVG_DIR}/<weight>/<name>-<weight>.svg")
    print(f"  PNGs: {PNG_DIR}/<weight>/<name>.png")

if __name__ == "__main__":
    main()
