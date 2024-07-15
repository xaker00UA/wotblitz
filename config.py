import json

with open("config.json", "r") as f:
    try:
        config = json.load(f)
    except:
        config = dict()

LIMITED = config.get("limited", 10)
APPLICATION_ID = config.get("application_id", "6645d2ba41b7ded38e934bd6fdd48d05")
DATABASE = config.get(
    "database", "mongodb+srv://test:1234@wotblitz.9ctju87.mongodb.net/"
)
SESSION = config.get("start_session", False)
CLANS = config.get("clans", [])
PLAYERS = config.get("players", [])
