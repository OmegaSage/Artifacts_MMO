import personal
import requests
import asyncio

CHARACTER_NAME = personal.CHARACTER_NAME
TOKEN = personal.TOKEN

# API endpoint for the move action
url = f"https://api.artifactsmmo.com/my/{CHARACTER_NAME}/action/move"

# Authentication headers — your token identifies you on the server
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# Target coordinates: move to tile (0, 1) where the chicken is
body = { "x": 0, "y": 1 }

try:
    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    if "error" in data:
        raise Exception(data["error"]["message"])

    destination = data["data"]["destination"]
    cooldown = data["data"]["cooldown"]

    print(f"✅ Moved to ({destination['x']}, {destination['y']}) on {destination['name']}")
    print(f"⏳ Cooldown started: {cooldown['total_seconds']} seconds")
except Exception as e:
    print(f"❌ {e}")

#attempting to merge movement and attack scripts
# first problem, Cooldowns... how to make it wait? Async?

url = f"https://api.artifactsmmo.com/my/{CHARACTER_NAME}/action/fight"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

try:
    response = requests.post(url, headers=headers)
    data = response.json()

    if "error" in data:
        raise Exception(data["error"]["message"])

    fight = data["data"]["fight"]
    fight_stats = fight["characters"][0]

    print("🏆 Fight won!" if fight["result"] == "win" else "💀 Fight lost!")
    print(f"⚔️  XP gained: {fight_stats['xp']} | HP remaining: {fight_stats['final_hp']}")

    if len(fight_stats["drops"]) > 0:
        drops_str = ", ".join([f"{d['quantity']}x {d['code']}" for d in fight_stats["drops"]])
        print(f"🎁 Loot dropped: {drops_str}")
except Exception as e:
    print(f"❌ {e}")
