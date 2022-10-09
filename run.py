import os
import requests
import psutil
import time

import pypresence
from pypresence import Presence

from dotenv import load_dotenv

load_dotenv()
roblox_token, roblox_user_id = os.environ.get("ROBLOX_TOKEN"), os.environ.get("ROBLOX_UID")

session = requests.Session()
cookies = {
    ".ROBLOSECURITY": roblox_token
}

rpc = Presence("822963115980881960")
rpc.connect()
current_rpc_state = "idle"

while True:
    try:
        process_active = (("RobloxPlayer" or "Roblox.exe") in (i.name() for i in psutil.process_iter()))
    except Exception:
        process_active = False
    if process_active:
        # game presence api
        presence_response = session.post(
            "https://presence.roblox.com/v1/presence/users",
            json={"userIds": [roblox_user_id]},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            cookies=cookies
        )
        presence_data = presence_response.json()

        if presence_data["userPresences"][0]["userPresenceType"] == 2:
            # game thumbnail api
            game_thumbnail_response = session.get(f"https://thumbnails.roblox.com/v1/games/icons?universeIds={presence_data['userPresences'][0]['universeId']}&returnPolicy=PlaceHolder&size=256x256&format=Png&isCircular=false")
            game_thumbnail_data = game_thumbnail_response.json()

            # user detail api
            user_details_response = session.get(f"https://users.roblox.com/v1/users/{roblox_user_id}")
            user_details_data = user_details_response.json()

            # user thumbnail api
            user_thumbnail_response = session.get(f"https://thumbnails.roblox.com/v1/users/avatar-bust?userIds={roblox_user_id}&size=100x100&format=Png&isCircular=false")
            user_thumbnail_data = user_thumbnail_response.json()

            target_state = {
                "state": "In-Game",
                "details": f"Playing {presence_data['userPresences'][0]['lastLocation']}",

                "large_image": game_thumbnail_data["data"][0]["imageUrl"],
                "large_text": presence_data['userPresences'][0]['lastLocation'],

                "small_image": user_thumbnail_data["data"][0]["imageUrl"],
                "small_text": user_details_data["displayName"],

                "buttons": [
                    {"label": "View Experience", "url": f"https://www.roblox.com/games/{presence_data['userPresences'][0]['placeId']}/game"}
                ]
            }
            
            # don't run the update method if the target state matches the current state
            if current_rpc_state != target_state:
                rpc.update(**target_state, start=time.time())
                current_rpc_state = target_state
        else:
            rpc.clear()
            current_rpc_state = "idle"
    else:
        rpc.clear()
        current_rpc_state = "idle"
    time.sleep(1)