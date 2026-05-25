import os, requests, json
from datetime import datetime
from pathlib import Path

SERVER = "Yokipakje.aternos.me:31247"
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
        content = "<@&1508480301289181235> De server is online!"
    else:
        embed = {"title":"🔴 Server is OFFLINE","description":f"**{SERVER}**\nDe server is gestopt.","color":0xE74C3C,"timestamp":datetime.utcnow().isoformat()}
        content = ""
    r = requests.post(WEBHOOK, json={"username":"Minecraft Status","content":content,"embeds":[embed]})
    print(f"Discord melding verstuurd! Status: {r.status_code}")

def load_state():
    try:
        data = json.loads(STATUS_FILE.read_text())
        return data.get("status", "offline"), data.get("offline_count", 0)
    except:
        return "offline", 0

def save_state(status, offline_count):
    STATUS_FILE.write_text(json.dumps({"status": status, "offline_count": offline_count}))

prev_status, offline_count = load_state()
print(f"Vorige status: {prev_status}, offline teller: {offline_count}")

online, sp, mx = check()

if online:
    offline_count = 0
    if prev_status == "offline":
        print("Server is ONLINE gekomen! Melding versturen...")
        send(True, sp, mx)
    else:
        print("Server is nog steeds online.")
    save_state("online", 0)
else:
    if prev_status == "online":
        offline_count += 1
        print(f"Server lijkt offline ({offline_count}/
