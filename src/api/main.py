from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import asyncio
import logging
import yaml
from pathlib import Path
from src.api.endpoints import router
from src.network.traffic_analyzer import alerts, start_analyzer, alert_manager
from src.network.packet_sniffer import get_active_interface, get_network_interfaces
from src.utils.helpers import setup_logging

# Setup logging
logger = setup_logging()

# Load configuration
def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

# Check for custom config path from environment variable or use default
import os
config_path = os.environ.get('CONFIG_PATH', 'config.yaml')
logger.info(f"Loading configuration from: {config_path}")
config = load_config(config_path)

app = FastAPI(
    title="IDS & IoT Security System",
    description="Real-time threat detection and monitoring system",
    version="1.0.0"
)

# Display network interface information on startup
@app.on_event("startup")
async def startup_event():
    """Display network interface information when the server starts."""
    try:
        interfaces = get_network_interfaces()
        logger.info("=" * 60)
        logger.info("Network Interface Information:")
        logger.info("=" * 60)

        for iface in interfaces:
            iface_type = "LOOPBACK" if iface['is_loopback'] else "EXTERNAL"
            logger.info(f"[{iface_type}] {iface['description']}")
            logger.info(f"  IP Address: {iface['ip']}")
            logger.info(f"  MAC Address: {iface['mac']}")
            logger.info(f"  Network: {iface['network']}")
            logger.info("-" * 60)

        external_ips = [iface['ip'] for iface in interfaces if not iface['is_loopback']]
        if external_ips:
            logger.info(f"External IP addresses: {', '.join(external_ips)}")
        else:
            logger.info("No external IP addresses found (only loopback)")

        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Failed to display network interface info: {e}")

# Add CORS middleware to allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# Start traffic analyzer with configuration
interface = config.get('network', {}).get('interface', None) or get_active_interface()
start_analyzer(interface=interface, config=config)

# Serve static files for the React app
@app.get("/{path:path}")
async def serve_spa(path: str):
    if path.startswith("api/") or path in ["ws/alerts", "ws/flows"]:
        raise HTTPException(status_code=404, detail="Not found")
    file_path = Path("src/frontend/dist") / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # For SPA, serve index.html for any non-API path
    index_path = Path("src/frontend/dist/index.html")
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Not found")

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()
flows_manager = ConnectionManager()

@app.websocket('/ws/alerts')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    last_alert_count = 0
    try:
        while True:
            await asyncio.sleep(1)  # Check for new alerts every second
            # Get alerts from alert_manager (the source of truth)
            current_alerts = alert_manager.get_alerts(limit=1)
            current_count = alert_manager.alert_counter

            # If there's a new alert, broadcast it
            if current_count > last_alert_count and current_alerts:
                await manager.broadcast(current_alerts[0])  # Send the latest alert
                last_alert_count = current_count
    except:
        manager.disconnect(websocket)

@app.websocket('/ws/flows')
async def websocket_flows_endpoint(websocket: WebSocket):
    await flows_manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # send flows every 1s
            from src.network.traffic_analyzer import flows
            flow_data = [{"key": k, "pkt_count": len(v['packets'])} for k, v in flows.items()]
            await websocket.send_json(flow_data)
    except:
        flows_manager.disconnect(websocket)
