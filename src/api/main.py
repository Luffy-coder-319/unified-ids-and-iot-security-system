from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
from src.api.endpoints import router
from src.network.traffic_analyzer import alerts

app = FastAPI()
app.include_router(router)

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

manager = ConnectionManager

@app.websocket('/ws/alerts')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(5) # poll for new alerts
            if alerts:
                await manager.broadcast(alerts[-1]) # send latest alert
    except:
        manager.disconnect(websocket)

# Simple HTML dashboard for demo; (use full frontend in production)
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head><title>Security Dashboard</title></head>
        <body>
            <h1>Real-Time Threats</h1>
            <div id="alerts"></div>
            <script>
                const ws = new WebSocket("ws://localhost:8000/ws/alerts");
                ws.onmessage = function(event) {
                    document.getElementById("alerts").innerHTML += "<p>" + event.data + "</p>";
                };
            </script>
        </body>
    </html>
    """
