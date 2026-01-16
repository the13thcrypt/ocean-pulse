import json
import asyncio
import websockets
import time
from config import AISSTREAM_API_KEY, BOUNDING_BOX

AIS_WS_URL = "wss://stream.aisstream.io/v0/stream"

LAST_SEEN = {}
MIN_INTERVAL = 5  # seconds per ship (VERY HIGH THROTTLE)

def extract_position(message):
    for key in (
        "PositionReport",
        "StandardClassBPositionReport",
        "ExtendedClassBPositionReport"
    ):
        if key in message:
            m = message[key]
            if "Latitude" not in m or "Longitude" not in m:
                return None

            mmsi = m["UserID"]
            now = time.time()

            if mmsi in LAST_SEEN and now - LAST_SEEN[mmsi] < MIN_INTERVAL:
                return None  # DROP UPDATE

            LAST_SEEN[mmsi] = now

            return {
                "mmsi": mmsi,
                "lat": m["Latitude"],
                "lon": m["Longitude"],
                "speed": m.get("Sog", 0)
            }
    return None

async def ais_stream(callback, status_cb):
    while True:
        try:
            status_cb("connecting")
            async with websockets.connect(
                AIS_WS_URL,
                ping_interval=30,
                ping_timeout=30
            ) as ws:

                status_cb("connected")

                await ws.send(json.dumps({
                    "APIKey": AISSTREAM_API_KEY,
                    "BoundingBoxes": [[
                        BOUNDING_BOX["lat_min"],
                        BOUNDING_BOX["lon_min"],
                        BOUNDING_BOX["lat_max"],
                        BOUNDING_BOX["lon_max"]
                    ]]
                }))

                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    ship = extract_position(data.get("Message", {}))
                    if ship:
                        await callback(ship)

        except Exception as e:
            status_cb("reconnecting")
            await asyncio.sleep(10)
