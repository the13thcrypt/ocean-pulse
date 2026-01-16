import uvicorn
import numpy as np
import asyncio
import json
import websockets
import os
import sys
import math
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from sklearn.cluster import DBSCAN

# --- 1. CONFIGURATION ---
AISSTREAM_KEY = "e7e664a1dfe3a934df6838ed6131c6ed4b7640ee"

app = FastAPI()
current_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(current_dir, "index.html")

# --- 2. PHYSICS ENGINE (Indian Ocean Current Model) ---
class DriftEngine:
    @staticmethod
    def get_forces(hour):
        # The Equatorial Counter Current (Flows East-West)
        # Ships here are in deep water, drift is strong and consistent.
        base_u = -0.025  # Strong Westward push
        base_v = -0.005  # Slight Southward push
        
        # Ocean Swell (Long period waves)
        tide_cycle = (hour / 12.0) * 2 * math.pi
        swell_strength = 0.015
        
        return base_u + (math.sin(tide_cycle) * swell_strength), base_v

    @staticmethod
    def analyze_risk(particles):
        endpoints = np.array([p[-1] for p in particles])
        if len(endpoints) < 3: return []
        
        # Cluster the endpoints
        clustering = DBSCAN(eps=0.02, min_samples=3).fit(endpoints)
        zones = []
        
        for label in set(clustering.labels_):
            if label == -1: continue 
            cluster = endpoints[clustering.labels_ == label]
            centroid = np.mean(cluster, axis=0)
            zones.append({
                "lat": float(centroid[0]), "lon": float(centroid[1]),
                "radius_km": float(len(cluster) * 0.5), 
                "risk_score": int(len(cluster))
            })
        return zones

    @staticmethod
    def run_ensemble(start_lat, start_lon):
        particles = []
        # Generate 15 particles per ship
        for i in range(15): 
            path = []
            curr_lat, curr_lon = start_lat, start_lon
            for hour in range(24):
                u, v = DriftEngine.get_forces(hour)
                # Add randomness (Wind/Waves)
                curr_lat += v + np.random.normal(0, 0.003)
                curr_lon += u + np.random.normal(0, 0.003)
                path.append([curr_lat, curr_lon])
            particles.append(path)
        return particles

# --- 3. SERVER ROUTES ---
@app.get("/")
@app.get("/index.html")
async def serve_ui():
    if os.path.exists(index_path): return FileResponse(index_path)
    return HTMLResponse("<h1>Error: index.html missing</h1>", status_code=404)

connected_clients = set()

@app.websocket("/ws/live-feed")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True: await asyncio.sleep(1)
    except:
        connected_clients.remove(websocket)

# --- 4. THE GUARANTEED DATA FEED ---
async def ais_listener():
    print("\n" + "="*60)
    print("📡  TARGETING: SRI LANKA SUPER-HIGHWAY (DONDRA HEAD)")
    print("🌊  STATUS: OPTIMIZED FOR FREE API LIMITS")
    print("="*60 + "\n")
    
    while True:
        try:
            async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ais_ws:
                sub_msg = {
                    "APIKey": AISSTREAM_KEY,
                    # 🎯 THE SWEET SPOT: Small box, but 100% traffic probability
                    # Lat 5.5 to 6.5 is the main shipping lane South of Sri Lanka
                    "BoundingBoxes": [[[5.5, 79.5], [6.5, 81.5]]], 
                    "FilterMessageTypes": ["PositionReport"]
                }
                await ais_ws.send(json.dumps(sub_msg))
                print("✅ CONNECTED. WAITING FOR TRAFFIC (Should be instant)...")
                
                async for message_json in ais_ws:
                    msg = json.loads(message_json)
                    if msg.get("MessageType") == "PositionReport":
                        data = msg["Message"]["PositionReport"]
                        
                        # Process physics
                        paths = DriftEngine.run_ensemble(data["Latitude"], data["Longitude"])
                        zones = DriftEngine.analyze_risk(paths)
                        
                        print(f"🚢 SHIP: {data['UserID']} | Loc: {data['Latitude']:.3f}, {data['Longitude']:.3f}")
                        
                        payload = {
                            "mmsi": data["UserID"],
                            "lat": data["Latitude"], "lon": data["Longitude"],
                            "trajectory": paths, "impact_zones": zones
                        }
                        
                        for client in list(connected_clients):
                            try: await client.send_json(payload)
                            except: pass

        except Exception as e:
            print(f"⚠️ RECONNECTING: {e}")
            await asyncio.sleep(2)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(ais_listener())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)