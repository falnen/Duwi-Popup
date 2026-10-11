import os
import sys
from pathlib import Path
import json
'''
Stores the user token in AppData so the user doesnt have to reconnect to twitch on every launch.
'''
def getUserAppDir():
    if sys.platform == "win32":
        base_dir = Path.home() / "AppData" / "Local" / "falnen" / "DUWI"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "falnen" / "DUWI"
    else:
        base_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share" / "falnen" / "DUWI"))
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir

def loadTokenFromFile():
    folder = getUserAppDir()
    file = folder / 'Token.json'
    file.touch()
    try:
        with open(file,'r',encoding='utf-8') as f:
            data = json.load(f)
        return data.get("Token")
    except:
        return None

def saveTokenToFile(token:str):
    folder = getUserAppDir()
    file = folder / 'Token.json'
    file.touch()
    with open(file,'w',encoding='utf-8') as f:
        json.dump({"Token":token},f)
        