import os, requests
from datetime import datetime
from mcstatus import JavaServer
from pathlib import Path

SERVER = os.environ["SERVER_ADDRESS"]
WEBHOOK = os.environ["WEBHOOK_URL"]
STATUS_FILE = Path("status.txt")

def check():
    try:
        print(f"Pinging {SERVER}...")
        s = JavaServer.lookup(SERVER).status()
        print(f"Server is ONLINE! Spelers: {s.players.online}/{s.players.max}")
        return True, s.players.online, s.players.max, s.motd.to_plain()
    except Exception as e:
        print(f"Server is OFFLINE of onbereikbaar: {e}")
        return False, 0, 0, ""

def send(online, spelers=0, mx=0, motd=""):
    if online:
        embed = {"title":"🟢 Server is ONLINE!","description":f"**{SERVER}**\nKom joinen!","color":0x2ECC71,"fields":[{"name":"🎮 Spelers","value":f"{spelers}/{mx}","inline":True}],"timestamp":datetime.utcnow().isoformat()}
    else:
        embed = {"title":"🔴 Server is OFFLINE","description":f"**{SERVER}**\nDe server is gestopt.","color":0xE74C3C,"timestamp":datetime.utcnow().isoformat()}
    r = requests.post(WEBHOOK, json={"username":"Minecraft Status","embeds":[embed]})
    print(f"Discord melding verstuurd! Status code: {r.status_code}")

prev = STATUS_FILE.read_text().strip() if STATUS_FILE.exists() else "offline"
print(f"Vorige status: {prev}")
online, sp, mx, motd = check()
cur = "online" if online else "offline"
print(f"Huidige status: {cur}")
if cur != prev:
    print("Status veranderd! Melding versturen...")
    send(online, sp, mx, motd)
else:
    print("Geen verandering, geen melding.")
STATUS_FILE.write_text(cur)
