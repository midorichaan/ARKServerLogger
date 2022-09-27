import re
from pathlib import Path
from datetime import datetime, timedelta, timezone

import aiohttp
import asyncio
import config

#vars
loop = asyncio.get_event_loop()
log_dir = "/home/midorichan/arkserver/ShooterGame/Saved/Logs"
UTC = timezone.utc
JST = timezone(timedelta(hours=+9), "JST")
dt_now = datetime.now(UTC)
paths = Path(log_dir)
log_arr = list(paths.glob("ServerGame*"))
log_dct = {}

print(f"Vars: log_arr: {log_arr}")

def main():
    global log_arr, log_dct, paths, dt_now, JST, UTC, log_dir

    for i in log_arr:
        log_dct[i] = i.stat().st_mtime
    log_arr = []

    for k,v in sorted(log_dct.items(), key=lambda x:x[1], reverse=True):
        log_arr.append(str(k))

    if not log_arr:
        print("No logs found")
        return

    with open(log_arr[0], encoding='utf-8') as f:
        l_strip = [s.strip() for s in f.readlines()]

    for item in l_strip:
        item_ext = re.sub(r'^.+\]\[[0-9]+\]','',item)
        m = re.match(r'^[0-9|\.|_]+', item_ext)

        if m:
            item_time = m.group()
            item_text = re.sub(r'^[0-9|\.|_]+: ','',item_ext)                       
            dt = datetime.strptime(item_time, '%Y.%m.%d_%H.%M.%S')
            dt_utc = dt.replace(tzinfo=UTC)
            dt_jst = dt_utc.astimezone(JST)
            delta_dt = dt_now - dt_utc

            if(delta_dt.total_seconds() <= 60): 
                data = {
                    "username": "ARK Server Log",
                    "avatar_url": "https://dl.pchan-sv.cf/kawaii-girl-1.jpg",
                    "embeds": [
                        {
                            "title": "ARK Logs",
                            "description": f"```\n{dt_jst.strftime('%Y-%m-%d %H:%M')}: {item_text}\n```"
                        }
                    ]
                }

                loop.run_until_complete(post_data(data))
        else:
            print("log not found")

async def post_data(data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.request(
            "POST",
            config.WEBHOOK,
            json=data
        ) as resp:
            if resp.status != 200:
                print(f"ERROR: DiscordAPI returns {resp.status}: {await resp.text()}")
            else:
                print(f"SUCCESS: Posted! {resp.status}")

if __name__ == "__main__":
    main()
    print("main called")
