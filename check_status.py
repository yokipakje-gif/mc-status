import os, requests
from datetime import datetime
from pathlib import Path

SERVER = "weasel.aternos.host:31247"
WEBHOOK = os.environ["WEBHOOK_URL"]
STATUS_FILE = Path("status.txt")

def check():
    try:
        url = f"https://api.mcstatus.io/v2/status/java/{SERVER}"
        print(f"Checking {url}")
        r = requests.get(url, timeout=15)
        data = r.json()
        print(f"Full response: online={data.get('online')}, players={data.get('players')}")
        if data.get("online"):
            players = data.get("players", {})
            return True, players.get("online", 0), players.get("max", 0)
        return False, 0, 0
    except Exception as e:
        print(f"Error: {e}")
        return False, 0, 0

def send(online, spelers=0, mx=0):
    if online:
        embed = {"title":"🟢 Server is ONLINE!","description":f"**{SERVER}**\nKom joinen!","color":0x2ECC71,"fields":[{"name":"🎮 Spelers","value":f"{spelers}/{mx}","inline":True}],"timestamp":datetime.utcnow().isoformat()}
    else:
        embed = {"title":"🔴 Server is OFFLINE","description":f"**{SERVER}**\nDe server is gestopt.","color":0xE74C3C,"timestamp":datetime.utcnow().isoformat()}
    r = requests.post(WEBHOOK, json={"username":"Minecraft Status","embeds":[embed]})
    print(f"Discord melding verstuurd! Status: {r.status_code}")

prev = STATUS_FILE.read_text().strip() if STATUS_FILE.exists() else "offline"
print(f"Vorige status: {prev}")
online, sp, mx = check()
cur = "online" if online else "offline"
print(f"Huidige status: {cur}")
if cur != prev:
    print("Status veranderd! Melding versturen...")
    send(online, sp, mx)
else:
    print("Geen verandering, geen melding.")
STATUS_FILE.write_text(cur)
