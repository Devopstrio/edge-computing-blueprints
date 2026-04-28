import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("edge-blueprints-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Edge Computing Blueprints API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/sites/register")
def register_site(site_id: str, location: str, hardware_spec: str):
    logger.info(f"Registering new edge site: {site_id} at {location}")
    return {"status": "REGISTERED", "site_id": site_id, "provisioning_url": f"https://provision.internal/sites/{site_id}"}

@app.get("/fleet/status")
def get_fleet_status():
    return {
        "total_sites": 1240,
        "online_sites": 1215,
        "offline_sites": 25,
        "update_in_progress": 12,
        "fleet_health": "98.2%"
    }

@app.post("/deployments/run")
def run_deployment(blueprint_id: str, target_sites: list):
    logger.info(f"Running deployment blueprint: {blueprint_id} to {len(target_sites)} sites")
    return {"status": "STARTED", "deployment_id": "dep_99_delta"}

@app.post("/updates/publish")
def publish_update(version: str, component: str):
    logger.info(f"Publishing fleet-wide update: {component} v{version}")
    return {"status": "PUBLISHED", "update_id": "up_77_gamma"}

@app.get("/scores/summary")
def get_scores_summary():
    return {
        "global_readiness_score": 0.94,
        "avg_update_success_rate": "99.2%",
        "connectivity_uptime": "99.95%",
        "fleet_rating": "OPTIMIZED"
    }

@app.get("/alerts")
def get_active_alerts():
    return [
        {"id": "alert-1", "severity": "CRITICAL", "message": "Site Offline: Warehouse-North-04 (Since 12m)"},
        {"id": "alert-2", "severity": "MEDIUM", "message": "High CPU Latency: Store-TX-88 (Edge AI Node)"}
    ]

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "total_managed_devices": 15420,
        "telemetry_processed_24h": "1.2TB",
        "active_ai_inferences": 450,
        "platform_status": "READY"
    }
