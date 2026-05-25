import os
import requests
import json
from datetime import datetime
from pathlib import Path

SERVER = "Yokipakje.aternos.me:31247"
WEBHOOK = os.environ.get("WEBHOOK_URL", "")
STATUS_FILE = Path("status.txt")
OFFLINE_THRESHOLD = 3


def check():
    try:
        url = "https://api.mcstatus.io/v2/status/java/" + SERVER
        print("Checking " + url)
        r = requests.get(url, timeout=15)
        data = r.json()
        is_online = data.get("online", False)
        players = data.get("players") or {}
        online_count = players.get("online", 0)
        max_count = players.get("max", 0)
        print("Response: online=" + str(is_online) + ", players=" + str(online_count) + "/" + str(max_count))
        return is_online, online_count, max_count
    except Exception as e:
        print("Error bij checken: " + str(e))
        return False, 0, 0


def send(online, spelers=0, mx=0):
    if not WEBHOOK:
        print("Geen webhook URL gevonden!")
        return
    if online:
        embed = {
            "title": "Server is ONLINE!",
            "description": "**" + SERVER + "**\nKom joinen!",
            "color": 3066993,
            "fields": [
                {"name": "Spelers", "value": str(spelers) + "/" + str(mx), "inline": True}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        content = "<@&1508480301289181235> De server is online!"
    else:
        embed = {
            "title": "Server is OFFLINE",
            "description": "**" + SERVER + "**\nDe server is gestopt.",
            "color": 15158332,
            "timestamp": datetime.utcnow().isoformat()
        }
        content = ""
    try:
        r = requests.post(WEBHOOK, json={"username": "Minecraft Status", "content": content, "embeds": [embed]})
        print("Discord melding verstuurd! Status: " + str(r.status_code))
    except Exception as e:
        print("Fout bij versturen Discord melding: " + str(e))


def load_state():
    if not STATUS_FILE.exists():
        return "offline", 0
    raw = STATUS_FILE.read_text().strip()
    if not raw:
        return "offline", 0
    try:
        data = json.loads(raw)
        return str(data.get("status", "offline")), int(data.get("offline_count", 0))
    except Exception:
        if "online" in raw:
            return "online", 0
        return "offline", 0


def save_state(status, offline_count):
    STATUS_FILE.write_text(json.dumps({"status": status, "offline_count": offline_count}))


prev_status, offline_count = load_state()
print("Vorige status: " + prev_status + ", offline teller: " + str(offline_count))

online, sp, mx = check()

if online:
    if prev_status == "offline":
        print("Server is ONLINE gekomen! Melding versturen...")
        send(True, sp, mx)
    else:
        print("Server is nog steeds online.")
    save_state("online", 0)
else:
    if prev_status == "online":
        offline_count = offline_count + 1
        print("Server lijkt offline (" + str(offline_count) + "/" + str(OFFLINE_THRESHOLD) + ")")
        if offline_count >= OFFLINE_THRESHOLD:
            print("3x achter elkaar offline, melding versturen...")
            send(False)
            save_state("offline", 0)
        else:
            save_state("online", offline_count)
    else:
        print("Server is nog steeds offline.")
        save_state("offline", 0)
