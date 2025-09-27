from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import pandas as pd
import numpy as np
import json

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry JSON at startup
DATA_PATH = Path(__file__).parent.parent / "q-vercel-latency.json"
try:
    with open(DATA_PATH) as f:
        telemetry_list = json.load(f)
    df = pd.DataFrame(telemetry_list)
except FileNotFoundError:
    df = pd.DataFrame(columns=["region", "latency_ms", "uptime"])  # fallback empty

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)

    results = {}

    for region in regions:
        region_data = df[df["region"] == region]
        if region_data.empty:
            results[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        avg_latency = float(region_data["latency_ms"].mean())
        p95_latency = float(np.percentile(region_data["latency_ms"], 95))
        avg_uptime = float(region_data["uptime"].mean())
        breaches = int((region_data["latency_ms"] > threshold_ms).sum())

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return JSONResponse(content=results)
