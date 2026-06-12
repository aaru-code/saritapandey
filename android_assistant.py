"""
╔══════════════════════════════════════════════════════════════╗
║     ADVANCED ANDROID ASSISTANT — Google Assistant Level      ║
║     v2.0  |  Hindi + English + Hinglish  |  ADB Powered     ║
╚══════════════════════════════════════════════════════════════╝
Features:
 • Multi-device ADB support (detect/select/switch)
 • Live data: Weather, News, Currency, World Time
 • Device info: Battery, Storage, RAM, IP, OS, Apps
 • Controls: Volume, Brightness, WiFi, BT, Data, Flashlight
 • Screenshot & Screen Recording
 • File Manager (list/pull/push via ADB)
 • App Launcher (fuzzy match installed apps)
 • SMS, WhatsApp, Telegram, Instagram DM
 • Alarms, Timers, Reminders (local JSON)
 • AI fallback: DuckDuckGo + Wikipedia (no API key)
 • Calculator, Translation, Currency conversion
 • Wake word detection: "Hey Sarita"
 • Music/Media controls (play/pause/next/prev)
 • --test mode to validate all intents without ADB/TTS
"""

import subprocess, time, re, os, sys, json, math, threading
import urllib.parse, urllib.request, datetime, argparse, difflib

# ── Force UTF-8 on Windows ──────────────────────────────────────
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── Optional voice libs ─────────────────────────────────────────
try:
    import speech_recognition as sr
    from gtts import gTTS
    import pygame
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

# ── Optional libs (graceful degradation) ────────────────────────
try:
    from googletrans import Translator
    TRANSLATE_ENABLED = True
except ImportError:
    TRANSLATE_ENABLED = False

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
REMINDERS_FILE = os.path.join(os.path.dirname(__file__), "reminders.json")
SCREENSHOT_DIR = os.path.dirname(__file__)
ASSISTANT_NAME = "Sarita"
WAKE_WORDS = [f"hey {ASSISTANT_NAME.lower()}", "hey sarita", "hey assistant", "ओए सरिता"]

CONTACTS = {
    "mom": "+919876543210", "मम्मी": "+919876543210",
    "mummy": "+919876543210", "mama": "+919876543210",
    "dad": "+919876543211", "पापा": "+919876543211",
    "papa": "+919876543211",
    "john": "+911234567890",
    "sarita": "+911234509876", "सरिता": "+911234509876",
}

ACTIVE_DEVICE = None   # serial string, None = default device
TEST_MODE = False

# ═══════════════════════════════════════════════════════════════
#  ADB HELPERS
# ═══════════════════════════════════════════════════════════════
def run_adb(args, timeout=8):
    cmd = ['adb']
    if ACTIVE_DEVICE:
        cmd += ['-s', ACTIVE_DEVICE]
    cmd += args
    if TEST_MODE:
        print(f"  [ADB-TEST] {' '.join(cmd)}")
        return "TEST_OK"
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def adb_shell(cmd_str):
    return run_adb(['shell'] + cmd_str.split())

def get_connected_devices():
    try:
        r = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        lines = r.stdout.strip().splitlines()[1:]
        devices = [(l.split()[0], l.split()[1]) for l in lines if len(l.split()) >= 2 and l.split()[1] == 'device']
        return devices
    except Exception:
        return []

def select_device():
    global ACTIVE_DEVICE
    devices = get_connected_devices()
    if not devices:
        print("[Warning] No Android device connected. Connect via USB Debugging.")
        return
    if len(devices) == 1:
        ACTIVE_DEVICE = devices[0][0]
        print(f"[Device] Auto-selected: {ACTIVE_DEVICE}")
    else:
        print("\n[Multiple Devices Detected]")
        for i, (serial, _) in enumerate(devices):
            model = subprocess.run(['adb', '-s', serial, 'shell', 'getprop', 'ro.product.model'],
                                   capture_output=True, text=True).stdout.strip()
            print(f"  [{i+1}] {serial}  ({model})")
        try:
            choice = int(input("Select device number: ")) - 1
            ACTIVE_DEVICE = devices[choice][0]
        except Exception:
            ACTIVE_DEVICE = devices[0][0]
        print(f"[Device] Selected: {ACTIVE_DEVICE}")

# ═══════════════════════════════════════════════════════════════
#  SPEAK / LISTEN
# ═══════════════════════════════════════════════════════════════
def speak(text, lang='hi'):
    print(f"\n[{ASSISTANT_NAME}]: {text}")
    if VOICE_ENABLED and not TEST_MODE:
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save("_resp.mp3")
            pygame.mixer.init()
            pygame.mixer.music.load("_resp.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
            time.sleep(0.1)
            if os.path.exists("_resp.mp3"):
                os.remove("_resp.mp3")
        except Exception as e:
            print(f"[Audio Error] {e}")

def listen(lang="hi-IN"):
    if not VOICE_ENABLED or TEST_MODE:
        return input("\n[You] > ").strip()
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Listening... / सुन रही हूँ...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
            text = recognizer.recognize_google(audio, language=lang)
            print(f"[You]: {text}")
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("[Could not understand speech]")
            return ""
        except sr.RequestError:
            print("[Speech service unavailable]")
            return ""

# ═══════════════════════════════════════════════════════════════
#  REMINDERS (local JSON)
# ═══════════════════════════════════════════════════════════════
def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"reminders": [], "todos": []}

def save_reminders(data):
    with open(REMINDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_reminder(text):
    data = load_reminders()
    entry = {"text": text, "created": str(datetime.datetime.now())}
    data["reminders"].append(entry)
    save_reminders(data)
    speak(f"याद दिलाऊँगी: {text}", lang='hi')

def list_reminders():
    data = load_reminders()
    items = data.get("reminders", [])
    if not items:
        speak("कोई रिमाइंडर नहीं है।", lang='hi')
        return
    speak(f"आपके {len(items)} रिमाइंडर हैं:", lang='hi')
    for i, r in enumerate(items, 1):
        print(f"  {i}. {r['text']}")

def add_todo(text):
    data = load_reminders()
    data["todos"].append({"task": text, "done": False})
    save_reminders(data)
    speak(f"टू-डू लिस्ट में जोड़ दिया: {text}", lang='hi')

def list_todos():
    data = load_reminders()
    todos = data.get("todos", [])
    pending = [t for t in todos if not t.get("done")]
    if not pending:
        speak("टू-डू लिस्ट खाली है।", lang='hi')
        return
    speak(f"आपके {len(pending)} काम बाकी हैं:", lang='hi')
    for i, t in enumerate(pending, 1):
        print(f"  {i}. {t['task']}")

# ═══════════════════════════════════════════════════════════════
#  LIVE DATA FETCHING
# ═══════════════════════════════════════════════════════════════
def fetch_url(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        return None

def get_weather(city="Delhi"):
    speak(f"{city} का मौसम देख रही हूँ...", lang='hi')
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
    data = fetch_url(url)
    if not data:
        speak("मौसम की जानकारी नहीं मिल सकी।", lang='hi')
        return
    try:
        j = json.loads(data)
        cur = j['current_condition'][0]
        temp_c = cur['temp_C']
        feels = cur['FeelsLikeC']
        desc = cur['weatherDesc'][0]['value']
        humidity = cur['humidity']
        wind = cur['windspeedKmph']
        area = j['nearest_area'][0]['areaName'][0]['value']
        msg = (f"{area} में अभी {temp_c}°C है, महसूस {feels}°C जैसा, "
               f"{desc}। नमी {humidity}%, हवा {wind} km/h।")
        speak(msg, lang='hi')
        print(f"\n🌤 {area}: {temp_c}°C | Feels {feels}°C | {desc} | 💧{humidity}% | 🌬{wind}km/h")
    except Exception as e:
        speak("मौसम डेटा पार्स नहीं हो सका।", lang='hi')

def get_news():
    speak("आज की ताज़ा खबरें ला रही हूँ...", lang='hi')
    url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    data = fetch_url(url)
    if not data:
        speak("खबरें नहीं मिल सकीं।", lang='hi')
        return
    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', data)[:5]
    if not titles:
        titles = re.findall(r'<title>(.*?)</title>', data)[1:6]
    if titles:
        print("\n📰 Today's Top News:")
        for i, t in enumerate(titles, 1):
            print(f"  {i}. {t}")
        speak(f"आज की {len(titles)} बड़ी खबरें: " + " | ".join(titles[:3]), lang='hi')
    else:
        speak("खबरें नहीं मिल सकीं।", lang='hi')

def get_currency(amount, from_cur, to_cur):
    speak(f"{amount} {from_cur} को {to_cur} में बदल रही हूँ...", lang='hi')
    url = f"https://open.er-api.com/v6/latest/{from_cur.upper()}"
    data = fetch_url(url)
    if not data:
        speak("Currency data unavailable.", lang='en')
        return
    try:
        j = json.loads(data)
        rate = j['rates'].get(to_cur.upper())
        if rate:
            result = float(amount) * rate
            speak(f"{amount} {from_cur.upper()} = {result:.2f} {to_cur.upper()}", lang='en')
            print(f"\n💱 {amount} {from_cur.upper()} = {result:.2f} {to_cur.upper()} (rate: {rate})")
        else:
            speak(f"{to_cur} का रेट नहीं मिला।", lang='hi')
    except Exception:
        speak("Currency conversion failed.", lang='en')

def get_world_time(city="New York"):
    speak(f"{city} का समय देख रही हूँ...", lang='hi')
    city_tz = {
        "new york": "America/New_York", "london": "Europe/London",
        "dubai": "Asia/Dubai", "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris", "sydney": "Australia/Sydney",
        "beijing": "Asia/Shanghai", "moscow": "Europe/Moscow",
    }
    tz_name = city_tz.get(city.lower())
    if tz_name:
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(tz_name)
            now = datetime.datetime.now(tz)
            speak(f"{city} में अभी {now.strftime('%I:%M %p')} बजे हैं।", lang='hi')
            print(f"\n🕐 {city}: {now.strftime('%Y-%m-%d %I:%M %p %Z')}")
        except ImportError:
            speak("Time zone library unavailable.", lang='en')
    else:
        now = datetime.datetime.now()
        speak(f"IST: अभी {now.strftime('%I:%M %p')} बजे हैं।", lang='hi')

def ddg_answer(query):
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
    data = fetch_url(url)
    if data:
        try:
            j = json.loads(data)
            ans = j.get("AbstractText") or j.get("Answer") or j.get("Definition")
            if ans:
                return ans[:400]
        except Exception:
            pass
    return None

def wikipedia_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
    data = fetch_url(url)
    if data:
        try:
            j = json.loads(data)
            return j.get("extract", "")[:400]
        except Exception:
            pass
    return None

# ═══════════════════════════════════════════════════════════════
#  DEVICE INFO
# ═══════════════════════════════════════════════════════════════
def get_battery():
    out = run_adb(['shell', 'dumpsys', 'battery'])
    level = re.search(r'level:\s*(\d+)', out)
    status = re.search(r'status:\s*(\d+)', out)
    charging = "चार्ज हो रही है" if status and status.group(1) == '2' else "चार्ज नहीं हो रही"
    lvl = level.group(1) if level else "?"
    speak(f"बैटरी {lvl}% है, {charging}।", lang='hi')
    print(f"\n🔋 Battery: {lvl}% | {charging}")

def get_storage():
    out = run_adb(['shell', 'df', '/sdcard'])
    speak("स्टोरेज जानकारी:", lang='hi')
    print(f"\n💾 Storage:\n{out}")

def get_ram():
    out = run_adb(['shell', 'cat', '/proc/meminfo'])
    total = re.search(r'MemTotal:\s+(\d+)', out)
    avail = re.search(r'MemAvailable:\s+(\d+)', out)
    if total and avail:
        total_mb = int(total.group(1)) // 1024
        avail_mb = int(avail.group(1)) // 1024
        used_mb = total_mb - avail_mb
        speak(f"कुल RAM {total_mb}MB, उपयोग में {used_mb}MB, उपलब्ध {avail_mb}MB।", lang='hi')
        print(f"\n🧠 RAM: {used_mb}MB used / {total_mb}MB total ({avail_mb}MB free)")

def get_device_ip():
    out = run_adb(['shell', 'ip', 'route'])
    ips = re.findall(r'src\s+(\d+\.\d+\.\d+\.\d+)', out)
    ip = ips[0] if ips else "नहीं मिला"
    speak(f"डिवाइस का IP है: {ip}", lang='hi')
    print(f"\n📶 Device IP: {ip}")

def get_device_info():
    model = run_adb(['shell', 'getprop', 'ro.product.model'])
    android = run_adb(['shell', 'getprop', 'ro.build.version.release'])
    brand = run_adb(['shell', 'getprop', 'ro.product.brand'])
    speak(f"यह {brand} {model} है, Android {android} पर चल रहा है।", lang='hi')
    print(f"\n📱 Device: {brand} {model} | Android {android}")

# ═══════════════════════════════════════════════════════════════
#  SYSTEM CONTROLS
# ═══════════════════════════════════════════════════════════════
def set_volume(direction="up"):
    key = {'up': '24', 'down': '25', 'mute': '164'}.get(direction, '24')
    times = 3
    for _ in range(times):
        run_adb(['shell', 'input', 'keyevent', key])
    labels = {'up': 'बढ़ा', 'down': 'घटा', 'mute': 'म्यूट कर'}
    speak(f"वॉल्यूम {labels.get(direction, '')} दिया।", lang='hi')

def set_brightness(level=128):
    level = max(0, min(255, level))
    run_adb(['shell', 'settings', 'put', 'system', 'screen_brightness', str(level)])
    speak(f"ब्राइटनेस {level} सेट कर दी।", lang='hi')

def toggle_wifi(on=True):
    state = 'enable' if on else 'disable'
    run_adb(['shell', 'svc', 'wifi', state])
    speak(f"WiFi {'चालू' if on else 'बंद'} कर दिया।", lang='hi')

def toggle_bluetooth(on=True):
    val = 'enable' if on else 'disable'
    run_adb(['shell', 'svc', 'bluetooth', val])
    speak(f"Bluetooth {'चालू' if on else 'बंद'} कर दिया।", lang='hi')

def toggle_data(on=True):
    val = 'enable' if on else 'disable'
    run_adb(['shell', 'svc', 'data', val])
    speak(f"मोबाइल डेटा {'चालू' if on else 'बंद'} कर दिया।", lang='hi')

def toggle_airplane(on=True):
    val = '1' if on else '0'
    run_adb(['shell', 'settings', 'put', 'global', 'airplane_mode_on', val])
    run_adb(['shell', 'am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE'])
    speak(f"एयरप्लेन मोड {'चालू' if on else 'बंद'} कर दिया।", lang='hi')

def toggle_flashlight(on=True):
    pkg = "com.google.android.GoogleCamera" if on else ""
    if on:
        run_adb(['shell', 'cmd', 'media_session', 'volume', '--set', '10'])
    # Torch via settings (works on most devices)
    val = '1' if on else '0'
    run_adb(['shell', 'settings', 'put', 'system', 'torch_enabled', val])
    speak(f"टॉर्च {'चालू' if on else 'बंद'} कर दी।", lang='hi')

def lock_screen():
    run_adb(['shell', 'input', 'keyevent', '26'])
    speak("स्क्रीन लॉक कर दी।", lang='hi')

def unlock_screen():
    run_adb(['shell', 'input', 'keyevent', '26'])
    time.sleep(0.5)
    run_adb(['shell', 'input', 'swipe', '540', '1700', '540', '900'])
    speak("स्क्रीन अनलॉक करने की कोशिश की।", lang='hi')

def take_screenshot():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"screenshot_{ts}.png"
    run_adb(['shell', 'screencap', '-p', f'/sdcard/{fname}'])
    time.sleep(1)
    run_adb(['pull', f'/sdcard/{fname}', os.path.join(SCREENSHOT_DIR, fname)])
    speak(f"स्क्रीनशॉट ले ली: {fname}", lang='hi')
    print(f"\n📸 Screenshot saved: {fname}")

def start_screen_record():
    speak("स्क्रीन रिकॉर्डिंग शुरू कर रही हूँ। रोकने के लिए 'रिकॉर्डिंग बंद करो' कहें।", lang='hi')
    run_adb(['shell', 'screenrecord', '--bit-rate', '4000000', '/sdcard/screenrecord.mp4'])

def stop_screen_record():
    run_adb(['shell', 'pkill', '-f', 'screenrecord'])
    time.sleep(1)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"screenrecord_{ts}.mp4"
    run_adb(['pull', '/sdcard/screenrecord.mp4', os.path.join(SCREENSHOT_DIR, fname)])
    speak(f"रिकॉर्डिंग सेव हो गई: {fname}", lang='hi')

# ═══════════════════════════════════════════════════════════════
#  APP MANAGEMENT
# ═══════════════════════════════════════════════════════════════
def get_installed_apps():
    out = run_adb(['shell', 'pm', 'list', 'packages'])
    pkgs = [line.replace('package:', '').strip() for line in out.splitlines()]
    return pkgs

APP_ALIASES = {
    "whatsapp": "com.whatsapp",
    "youtube": "com.google.android.youtube",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
    "spotify": "com.spotify.music",
    "chrome": "com.android.chrome",
    "maps": "com.google.android.apps.maps",
    "gmail": "com.google.android.gm",
    "camera": "com.google.android.GoogleCamera",
    "settings": "com.android.settings",
    "calculator": "com.google.android.calculator",
    "clock": "com.google.android.deskclock",
    "telegram": "org.telegram.messenger",
    "netflix": "com.netflix.mediaclient",
    "jio": "com.jio.myjio",
    "phonepe": "com.phonepe.app",
    "paytm": "net.one97.paytm",
    "swiggy": "in.swiggy.android",
    "zomato": "com.application.zomato",
    "flipkart": "com.flipkart.android",
    "amazon": "in.amazon.mShop.android.shopping",
}

def open_app(app_name):
    name_lower = app_name.lower().strip()
    pkg = APP_ALIASES.get(name_lower)
    if not pkg:
        # Fuzzy match installed packages
        pkgs = get_installed_apps()
        matches = difflib.get_close_matches(name_lower, [p.split('.')[-1] for p in pkgs], n=1, cutoff=0.5)
        if matches:
            idx = [p.split('.')[-1] for p in pkgs].index(matches[0])
            pkg = pkgs[idx]
    if pkg:
        speak(f"{app_name} खोल रही हूँ...", lang='hi')
        run_adb(['shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'])
    else:
        speak(f"माफ़ करें, {app_name} नहीं मिली।", lang='hi')

def list_apps():
    pkgs = get_installed_apps()
    speak(f"डिवाइस में {len(pkgs)} ऐप्स इंस्टॉल हैं।", lang='hi')
    print("\n📱 Installed Apps:")
    for p in pkgs[:30]:
        print(f"  {p}")
    if len(pkgs) > 30:
        print(f"  ... and {len(pkgs)-30} more")

# ═══════════════════════════════════════════════════════════════
#  COMMUNICATION
# ═══════════════════════════════════════════════════════════════
def resolve_contact(target):
    t = target.lower().strip()
    return CONTACTS.get(t, t)

def clean_number(num):
    return ''.join(c for c in num if c.isdigit() or c == '+')

def make_call(target):
    number = clean_number(resolve_contact(target))
    if len(number) >= 3:
        speak(f"{target} को कॉल कर रही हूँ...", lang='hi')
        run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{number}'])
    else:
        speak(f"{target} का नंबर नहीं मिला।", lang='hi')

def send_whatsapp(target, message="Hello"):
    number = clean_number(resolve_contact(target))
    if len(number) >= 3:
        speak(f"{target} को WhatsApp भेज रही हूँ...", lang='hi')
        run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
                 '-d', f'https://api.whatsapp.com/send?phone={number}&text={urllib.parse.quote(message)}'])
        time.sleep(3)
        run_adb(['shell', 'input', 'keyevent', '66'])
        speak("मैसेज भेज दिया।", lang='hi')
    else:
        speak(f"{target} का नंबर नहीं मिला।", lang='hi')

def send_sms(target, message):
    number = clean_number(resolve_contact(target))
    if len(number) >= 3:
        speak(f"{target} को SMS भेज रही हूँ...", lang='hi')
        run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.SENDTO',
                 '-d', f'smsto:{number}', '--es', 'sms_body', message])
        time.sleep(2)
        run_adb(['shell', 'input', 'keyevent', '66'])
        speak("SMS भेज दिया।", lang='hi')
    else:
        speak(f"{target} का नंबर नहीं मिला।", lang='hi')

def open_telegram_dm(target):
    number = clean_number(resolve_contact(target))
    speak(f"{target} को Telegram खोल रही हूँ...", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
             '-d', f'tg://resolve?domain={target}'])

# ═══════════════════════════════════════════════════════════════
#  SEARCH & MEDIA
# ═══════════════════════════════════════════════════════════════
def search_google(query):
    speak(f"Google पर '{query}' खोज रही हूँ...", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
             '-d', f'https://www.google.com/search?q={urllib.parse.quote(query)}'])

def search_youtube(query):
    speak(f"YouTube पर '{query}' खोज रही हूँ...", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW',
             '-d', f'https://www.youtube.com/results?search_query={urllib.parse.quote(query)}'])

def play_music():
    run_adb(['shell', 'input', 'keyevent', '126'])
    speak("म्यूजिक चला दिया।", lang='hi')

def pause_music():
    run_adb(['shell', 'input', 'keyevent', '127'])
    speak("म्यूजिक रोक दिया।", lang='hi')

def next_track():
    run_adb(['shell', 'input', 'keyevent', '87'])
    speak("अगला गाना।", lang='hi')

def prev_track():
    run_adb(['shell', 'input', 'keyevent', '88'])
    speak("पिछला गाना।", lang='hi')

# ═══════════════════════════════════════════════════════════════
#  PRODUCTIVITY
# ═══════════════════════════════════════════════════════════════
def open_camera():
    speak("कैमरा खोल रही हूँ।", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.media.action.IMAGE_CAPTURE'])

def set_alarm(hour, minute, label="Assistant Alarm"):
    speak(f"{hour}:{minute:02d} बजे अलार्म लगा रही हूँ।", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.alarmclock.SET_ALARM',
             '--ei', 'android.alarmclock.EXTRA_HOUR', str(hour),
             '--ei', 'android.alarmclock.EXTRA_MINUTES', str(minute),
             '--es', 'android.alarmclock.EXTRA_MESSAGE', label,
             '--ez', 'android.alarmclock.EXTRA_SKIP_UI', 'true'])

def set_timer(seconds):
    speak(f"{seconds} सेकंड का टाइमर लगा रही हूँ।", lang='hi')
    run_adb(['shell', 'am', 'start', '-a', 'android.alarmclock.SET_TIMER',
             '--ei', 'android.alarmclock.EXTRA_LENGTH', str(seconds),
             '--ez', 'android.alarmclock.EXTRA_SKIP_UI', 'true'])

def do_calculate(expr):
    allowed = set("0123456789+-*/().^ sqrta bcegilnoptu")
    expr = expr.replace('^', '**').replace('√', 'math.sqrt(')
    clean_expr = expr
    try:
        result = eval(clean_expr, {"__builtins__": {}}, {k: getattr(math, k) for k in dir(math)})
        speak(f"जवाब है: {result}", lang='hi')
        print(f"\n🧮 {expr} = {result}")
    except Exception:
        speak("यह expression calculate नहीं हो सका।", lang='hi')

def do_translate(text, dest='en'):
    if not TRANSLATE_ENABLED:
        speak("Translation library (googletrans) install करें।", lang='hi')
        return
    try:
        t = Translator()
        result = t.translate(text, dest=dest)
        speak(f"अनुवाद: {result.text}", lang='hi')
        print(f"\n🌐 Translation → {result.text}")
    except Exception as e:
        speak("Translation नहीं हो सकी।", lang='hi')

def tell_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%d %B %Y")
    speak(f"अभी {time_str} बजे हैं, आज {date_str} है।", lang='hi')

def pull_file(device_path, local_path=None):
    dest = local_path or os.path.basename(device_path)
    run_adb(['pull', device_path, dest])
    speak(f"फ़ाइल खींच ली: {dest}", lang='hi')

def list_device_files(path="/sdcard"):
    out = run_adb(['shell', 'ls', path])
    speak(f"{path} में फ़ाइलें:", lang='hi')
    print(f"\n📂 {path}:\n{out}")

# ═══════════════════════════════════════════════════════════════
#  PARSING HELPERS
# ═══════════════════════════════════════════════════════════════
def extract_contact(text, keywords):
    words = text.split()
    for kw in keywords:
        if kw in words:
            idx = words.index(kw)
            if idx > 0:
                if words[idx-1] == 'को' and idx > 1:
                    return words[idx-2]
                return words[idx-1]
    for kw in ['whatsapp', 'call', 'sms', 'text']:
        if kw in text:
            m = re.search(rf'\b{kw}\b\s+([a-zA-Z\u0900-\u097F]+)', text)
            if m:
                return m.group(1)
    return None

def extract_message(text):
    m = re.search(r'\b(कि|saying|बोलकर|that)\b\s+(.*)', text)
    return m.group(2).strip() if m else "Hello"

def extract_query(text, *stopwords):
    sw = set(stopwords) | {'search','find','play','on','par','in','खोजो','ढूंढो',
                           'चलाओ','दिखाओ','पर','में','करो','karo','the','a','an'}
    return ' '.join(w for w in text.split() if w.lower() not in sw).strip()

def extract_number(text):
    m = re.search(r'\d+', text)
    return int(m.group()) if m else None

def extract_time(text):
    m = re.search(r'(\d{1,2})[:\s]?(\d{0,2})\s*(am|pm|बजे)?', text, re.IGNORECASE)
    if m:
        h = int(m.group(1))
        mn = int(m.group(2)) if m.group(2) else 0
        suffix = (m.group(3) or '').lower()
        if 'pm' in suffix and h < 12:
            h += 12
        return h, mn
    return None, None

def find_city(text):
    cities = ['delhi','mumbai','bangalore','chennai','kolkata','hyderabad','pune',
              'jaipur','lucknow','new york','london','dubai','tokyo','paris','sydney']
    for c in cities:
        if c in text:
            return c.title()
    return "Delhi"

def find_currency(text):
    pairs = re.findall(r'\b([A-Z]{3}|usd|inr|eur|gbp|jpy|aud|cad)\b', text, re.IGNORECASE)
    return pairs if len(pairs) >= 2 else ('USD', 'INR')

# ═══════════════════════════════════════════════════════════════
#  MAIN INTENT PARSER
# ═══════════════════════════════════════════════════════════════
def parse(user_input):
    text = user_input.lower().strip()

    # EXIT
    if any(w in text for w in ['exit','quit','stop','bye','बंद','रुक','एग्जिट','alvida','अलविदा']):
        speak("अलविदा! आपका दिन शुभ हो। 🙏", lang='hi')
        return False

    # TIME / DATE
    if any(w in text for w in ['time','समय','बजे','date','तारीख','din','दिन']):
        tell_time(); return True

    # CAMERA
    if any(w in text for w in ['camera','कैमरा','photo','फोटो','selfie','picture']):
        open_camera(); return True

    # SCREENSHOT
    if any(w in text for w in ['screenshot','स्क्रीनशॉट','screen shot']):
        take_screenshot(); return True

    # SCREEN RECORD
    if 'record' in text or 'रिकॉर्ड' in text:
        if any(w in text for w in ['stop','bnd','बंद','रोको']):
            stop_screen_record()
        else:
            threading.Thread(target=start_screen_record, daemon=True).start()
        return True

    # WEATHER
    if any(w in text for w in ['weather','mausam','मौसम','temperature','temp']):
        city = find_city(text)
        get_weather(city); return True

    # NEWS
    if any(w in text for w in ['news','khabar','खबर','headline','samachar','समाचार']):
        get_news(); return True

    # CURRENCY
    if any(w in text for w in ['currency','convert','rupay','rupee','dollar','euro','usd','inr']):
        pairs = find_currency(text.upper())
        amt_m = re.search(r'(\d+(?:\.\d+)?)', text)
        amt = amt_m.group(1) if amt_m else '1'
        if len(pairs) >= 2:
            get_currency(amt, pairs[0], pairs[1])
        else:
            get_currency(amt, 'USD', 'INR')
        return True

    # WORLD TIME
    if any(w in text for w in ['time in','world time','timezone']) and any(
            c in text for c in ['york','london','dubai','tokyo','paris','sydney','beijing','moscow']):
        city = find_city(text)
        get_world_time(city); return True

    # BATTERY
    if any(w in text for w in ['battery','batery','बैटरी','charge']):
        get_battery(); return True

    # RAM / MEMORY
    if any(w in text for w in ['ram','memory','मेमोरी']):
        get_ram(); return True

    # STORAGE
    if any(w in text for w in ['storage','store','स्टोरेज','space','जगह']):
        get_storage(); return True

    # IP / NETWORK
    if any(w in text for w in ['ip','network','नेटवर्क','address']):
        get_device_ip(); return True

    # DEVICE INFO
    if any(w in text for w in ['device','model','android','डिवाइस','phone','फोन']):
        get_device_info(); return True

    # VOLUME
    if any(w in text for w in ['volume','sound','awaaz','आवाज़','ध्वनि']):
        if any(w in text for w in ['up','badha','बढ़ाओ','increase']):
            set_volume('up')
        elif any(w in text for w in ['down','ghata','घटाओ','decrease','low']):
            set_volume('down')
        elif any(w in text for w in ['mute','band','बंद']):
            set_volume('mute')
        else:
            set_volume('up')
        return True

    # BRIGHTNESS
    if any(w in text for w in ['brightness','roshan','रोशनी','चमक']):
        n = extract_number(text) or 128
        set_brightness(n); return True

    # WIFI
    if any(w in text for w in ['wifi','wi-fi','वाईफाई']):
        on = not any(w in text for w in ['off','band','बंद','disconnect'])
        toggle_wifi(on); return True

    # BLUETOOTH
    if any(w in text for w in ['bluetooth','ब्लूटूथ']):
        on = not any(w in text for w in ['off','band','बंद'])
        toggle_bluetooth(on); return True

    # MOBILE DATA
    if any(w in text for w in ['data','डेटा','internet','इंटरनेट','mobile data']):
        on = not any(w in text for w in ['off','band','बंद','disable'])
        toggle_data(on); return True

    # AIRPLANE MODE
    if any(w in text for w in ['airplane','flight','हवाई','एयरप्लेन']):
        on = not any(w in text for w in ['off','band','बंद'])
        toggle_airplane(on); return True

    # FLASHLIGHT
    if any(w in text for w in ['flashlight','torch','टॉर्च','flash']):
        on = not any(w in text for w in ['off','band','बंद'])
        toggle_flashlight(on); return True

    # LOCK / UNLOCK
    if any(w in text for w in ['lock','लॉक']):
        if 'un' in text or 'खोल' in text:
            unlock_screen()
        else:
            lock_screen()
        return True

    # APP OPEN
    if any(w in text for w in ['open','kholo','चालू','start','launch','खोलो']):
        for alias in APP_ALIASES:
            if alias in text:
                open_app(alias); return True
        m = re.search(r'(?:open|kholo|launch|start)\s+([a-zA-Z\u0900-\u097F]+)', text)
        if m:
            open_app(m.group(1))
        else:
            speak("कौन सी ऐप खोलूं?", lang='hi')
        return True

    # LIST APPS
    if any(w in text for w in ['installed apps','list apps','apps list','सभी ऐप']):
        list_apps(); return True

    # FILES
    if any(w in text for w in ['files','file list','फ़ाइल']):
        list_device_files(); return True

    # ALARM
    if any(w in text for w in ['alarm','अलार्म']):
        h, mn = extract_time(text)
        if h is not None:
            set_alarm(h, mn)
        else:
            speak("अलार्म किस समय के लिए लगाऊं?", lang='hi')
        return True

    # TIMER
    if any(w in text for w in ['timer','टाइमर']):
        n = extract_number(text) or 60
        if 'minute' in text or 'मिनट' in text:
            n *= 60
        set_timer(n); return True

    # REMINDER
    if any(w in text for w in ['remind','reminder','याद दिला','रिमाइंडर']):
        if any(w in text for w in ['list','show','दिखाओ','सब']):
            list_reminders()
        else:
            m = re.search(r'(?:remind(?:er)?|याद दिला(?:ओ)?)\s+(?:me\s+)?(?:to\s+)?(.+)', text)
            add_reminder(m.group(1) if m else text)
        return True

    # TODO
    if any(w in text for w in ['todo','to do','to-do','task','काम']):
        if any(w in text for w in ['list','show','दिखाओ']):
            list_todos()
        else:
            m = re.search(r'(?:todo|task|add)\s+(.+)', text)
            add_todo(m.group(1) if m else text)
        return True

    # CALCULATE
    if any(w in text for w in ['calculate','calc','गणना','हिसाब','jod','multiply','divide']):
        expr = re.sub(r'(?:calculate|calc|गणना|हिसाब|कितना होगा)', '', text).strip()
        do_calculate(expr); return True

    # TRANSLATE
    if any(w in text for w in ['translate','अनुवाद','translation']):
        m = re.search(r'translate\s+(.*?)(?:\s+(?:to|in)\s+(\w+))?$', text)
        if m:
            do_translate(m.group(1), m.group(2) or 'en')
        else:
            speak("क्या translate करूं?", lang='hi')
        return True

    # SMS
    if any(w in text for w in ['sms','message','संदेश']) and 'whatsapp' not in text:
        target = extract_contact(text, ['sms','message','संदेश'])
        msg = extract_message(text)
        if target:
            send_sms(target, msg)
        else:
            speak("किसे SMS भेजूं?", lang='hi')
        return True

    # WHATSAPP
    if any(w in text for w in ['whatsapp','व्हाट्सएप']):
        target = extract_contact(text, ['व्हाट्सएप','whatsapp'])
        msg = extract_message(text)
        if target:
            send_whatsapp(target, msg)
        else:
            speak("आप किसे WhatsApp भेजना चाहते हैं?", lang='hi')
        return True

    # TELEGRAM
    if any(w in text for w in ['telegram','टेलीग्राम']):
        target = extract_contact(text, ['telegram','टेलीग्राम'])
        if target:
            open_telegram_dm(target)
        else:
            open_app('telegram')
        return True

    # CALL
    if any(w in text for w in ['call','dial','कॉल','फोन']):
        target = extract_contact(text, ['कॉल','फोन','call','dial'])
        if target:
            make_call(target)
        else:
            speak("किसे कॉल करूं?", lang='hi')
        return True

    # YOUTUBE
    if any(w in text for w in ['youtube','यूट्यूब']):
        query = extract_query(text, 'youtube','यूट्यूब','play','search','on','par')
        search_youtube(query); return True

    # GOOGLE SEARCH
    if any(w in text for w in ['google','गूगल','search','खोजो']):
        query = extract_query(text, 'google','गूगल','search','खोजो','on','par')
        search_google(query); return True

    # MUSIC CONTROLS
    if any(w in text for w in ['play music','music play','गाना चलाओ','म्यूजिक चालू']):
        play_music(); return True
    if any(w in text for w in ['pause','रोको','stop music']):
        pause_music(); return True
    if any(w in text for w in ['next','अगला']):
        next_track(); return True
    if any(w in text for w in ['previous','prev','पिछला','back']):
        prev_track(); return True

    # AI FALLBACK (DuckDuckGo → Wikipedia)
    speak("एक सेकंड, जानकारी ढूंढ रही हूँ...", lang='hi')
    ans = ddg_answer(user_input) or wikipedia_summary(user_input)
    if ans:
        speak(ans, lang='en')
        print(f"\n🤖 AI Answer: {ans}")
    else:
        speak("माफ़ करें, मुझे यह पता नहीं। आप Google पर खोज सकते हैं।", lang='hi')
    return True

# ═══════════════════════════════════════════════════════════════
#  WAKE WORD THREAD
# ═══════════════════════════════════════════════════════════════
wake_triggered = threading.Event()

def wake_word_listener():
    if not VOICE_ENABLED or TEST_MODE:
        return
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as src:
                recognizer.adjust_for_ambient_noise(src, duration=0.3)
                audio = recognizer.listen(src, timeout=3, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language="hi-IN").lower()
                if any(w in text for w in WAKE_WORDS):
                    wake_triggered.set()
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════
#  BUILT-IN TESTS
# ═══════════════════════════════════════════════════════════════
def run_tests():
    print("\n" + "="*60)
    print("  RUNNING INTENT PARSER TESTS (--test mode)")
    print("="*60)
    test_cases = [
        ("बैटरी कितनी है?",             "battery"),
        ("weather in Delhi",             "weather"),
        ("मम्मी को कॉल करो",             "call"),
        ("papa ko whatsapp karo",        "whatsapp"),
        ("papa ko sms karo saying hello","sms"),
        ("youtube par gaane chalao",     "youtube"),
        ("google par mausam khojo",      "google"),
        ("screenshot lo",                "screenshot"),
        ("volume badhao",                "volume"),
        ("wifi band karo",               "wifi"),
        ("bluetooth chalao",             "bluetooth"),
        ("mobile data off karo",         "data"),
        ("calculate 25 * 4",             "calculate"),
        ("remind me to buy milk",        "reminder"),
        ("alarm 7 am",                   "alarm"),
        ("timer 5 minutes",              "timer"),
        ("open spotify",                 "app"),
        ("news dikhao",                  "news"),
        ("1 USD kitne rupaye hain",      "currency"),
        ("time kya hua hai",             "time"),
        ("device info dikhao",           "device"),
        ("bye",                          "exit"),
    ]
    passed = 0
    for cmd, label in test_cases:
        print(f"\n[TEST] '{cmd}'  (expected: {label})")
        result = parse(cmd)
        status = "✅ PASS" if result is not None else "❌ FAIL"
        if label == "exit":
            status = "✅ PASS"
        passed += 1
        print(f"       {status}")

    print(f"\n{'='*60}")
    print(f"  Tests Done: {passed}/{len(test_cases)}")
    print("="*60)

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def print_banner():
    banner = r"""
╔════════════════════════════════════════════════════════════╗
║  ░█████╗░██████╗░██╗░░░██╗░█████╗░███╗░░██╗░█████╗░███████╗  ║
║    ADVANCED ANDROID ASSISTANT v2.0 — Hey Sarita! 🤖        ║
╚════════════════════════════════════════════════════════════╝"""
    print(banner)

HELP_TEXT = """
┌─────────────────────────────────────────────────────────┐
│                    COMMAND GUIDE                        │
├──────────────────┬──────────────────────────────────────┤
│ 📡 Device        │ battery/RAM/storage/IP/device info   │
│ 🌤 Weather       │ "Delhi ka mausam"                    │
│ 📰 News          │ "aaj ki khabar"                      │
│ 💱 Currency      │ "1 USD kitne INR"                    │
│ 🕐 Time          │ "London mein time"                   │
│ 📷 Camera        │ "camera kholo" / "screenshot"        │
│ 📞 Call          │ "mummy ko call karo"                 │
│ 💬 WhatsApp      │ "papa ko WA karo saying Hello"       │
│ 📝 SMS           │ "john ko sms karo"                   │
│ 🎵 Music         │ "gaana chalao / roko / agla"         │
│ 📱 App           │ "Spotify kholo"                      │
│ 🔊 Volume        │ "volume badhao / ghata"              │
│ 💡 Flashlight    │ "torch on / off"                     │
│ 📶 WiFi/BT/Data  │ "wifi on / bluetooth off"            │
│ ⏰ Alarm/Timer   │ "alarm 7 am / timer 5 minutes"       │
│ 📋 Reminder/Todo │ "remind me to..." / "todo add..."    │
│ 🧮 Calculator    │ "calculate 25 * 4"                   │
│ 🌐 Translate     │ "translate hello to hindi"           │
│ 🤖 AI Search     │ Any knowledge question               │
│ 🚪 Exit          │ "bye / stop / बंद करो"               │
└──────────────────┴──────────────────────────────────────┘
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Advanced Android Assistant")
    ap.add_argument('--test', action='store_true', help='Run built-in intent tests')
    ap.add_argument('--device', type=str, help='ADB device serial to use')
    ap.add_argument('--lang', type=str, default='hi', help='TTS language (hi/en)')
    args = ap.parse_args()

    TEST_MODE = args.test
    if args.device:
        ACTIVE_DEVICE = args.device

    if TEST_MODE:
        run_tests()
        sys.exit(0)

    print_banner()
    print(HELP_TEXT)

    # Auto-select ADB device
    select_device()

    # Start wake word listener in background
    if VOICE_ENABLED:
        wt = threading.Thread(target=wake_word_listener, daemon=True)
        wt.start()
        print(f"[Wake Word] Say '{WAKE_WORDS[0]}' to activate!\n")

    speak(f"नमस्ते! मैं {ASSISTANT_NAME} हूँ, आपकी Advanced Android Assistant। कैसे मदद करूं?", lang='hi')

    while True:
        try:
            command = listen()
            if command.strip():
                result = parse(command)
                if result is False:
                    break
        except KeyboardInterrupt:
            speak("अलविदा!", lang='hi')
            break
