# Deployment Guide

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 10GB free space
- **Network**: Requires root/NET_RAW capability for packet capture

### Software Requirements
- **Python**: 3.12+
- **Node.js**: 20+ (for frontend development)
- **Docker**: 20.10+ (for containerized deployment)

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Using Docker Compose
```bash
# 1. Clone the repository
git clone <repository-url>
cd unified-ids-and-iot-security-system

# 2. Create .env file from template
cp .env.example .env
# Edit .env with your credentials

# 3. Build and run
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop the system
docker-compose down
```

#### Using Docker Only
```bash
# Build the image
docker build -t ids-system .

# Run the container
docker run -d \
  --name unified-ids \
  --cap-add=NET_RAW \
  --cap-add=NET_ADMIN \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config.yaml:/app/config.yaml \
  --env-file .env \
  ids-system

# View logs
docker logs -f unified-ids

# Stop the container
docker stop unified-ids
```

### Option 2: Manual Deployment

#### Backend Setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the system
cp .env.example .env
# Edit .env and config.yaml with your settings

# 4. Run the backend (requires root for packet capture)
sudo venv/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

#### Frontend Setup (Development)
```bash
# 1. Navigate to frontend directory
cd src/frontend

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

#### Frontend Setup (Production)
```bash
# 1. Build the frontend
cd src/frontend
npm install
npm run build

# 2. The built files are in src/frontend/dist/
# They will be served by the FastAPI backend
```

### Option 3: Systemd Service (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/unified-ids.service
```

Add the following content:

```ini
[Unit]
Description=Unified IDS and IoT Security System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/unified-ids-and-iot-security-system
Environment="PATH=/path/to/unified-ids-and-iot-security-system/venv/bin"
ExecStart=/path/to/unified-ids-and-iot-security-system/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable unified-ids
sudo systemctl start unified-ids
sudo systemctl status unified-ids
```

## Configuration

### Environment Variables (.env)

```bash
# Email Notifications
EMAIL_PASSWORD=your-app-password

# SMS Notifications (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
```

### System Configuration (config.yaml)

```yaml
app:
  host: "0.0.0.0"
  port: 8000

network:
  interface: "lo"  # Use "eth0" for production

ml:
  model_path: "trained_models/best_baseline.pkl"
  scaler_path: "trained_models/scaler_standard.pkl"
  encoder_path: "trained_models/encoder.pkl"

notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your-email@gmail.com"
    recipients:
      - "security-team@example.com"

  sms:
    enabled: false
    from_number: "+1234567890"
    recipients:
      - "+1234567890"

response_actions:
  enabled: true
  auto_block_high_severity: true
  temp_block_duration: 3600
```

## Accessing the System

- **Dashboard**: http://localhost:5173 (development) or http://localhost:8000 (production)
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket Alerts**: ws://localhost:8000/ws/alerts
- **WebSocket Flows**: ws://localhost:8000/ws/flows

## Network Interface Configuration

### For Production (External Traffic)
Edit `config.yaml`:
```yaml
network:
  interface: "eth0"  # Your actual network interface
```

### For Testing (Loopback)
Edit `config.yaml`:
```yaml
network:
  interface: "lo"
```

Find your network interface:
```bash
ip addr show
# or
ifconfig
```

## Security Considerations

1. **Root Privileges**: Required for packet capture
2. **Firewall**: Ensure port 8000 is accessible
3. **HTTPS**: Use a reverse proxy (nginx/apache) for HTTPS in production
4. **Credentials**: Never commit `.env` file to git
5. **Network Isolation**: Use Docker networks or VLANs for isolation

## Monitoring and Logs

### View Logs
```bash
# Docker
docker logs -f unified-ids

# Manual deployment
tail -f logs/app.log
tail -f logs/alerts.jsonl
```

### Health Check
```bash
# Check API status
curl http://localhost:8000/api/alerts

# Check system health
curl http://localhost:8000/api/statistics/summary
```

## Troubleshooting

### Packet Capture Not Working
- Ensure running with root privileges
- Check network interface name in config.yaml
- Verify NET_RAW capability (Docker)

### Frontend Not Loading
- Check if backend is running on port 8000
- Verify CORS is enabled in src/api/main.py
- Check browser console for errors

### Models Not Loading
- Ensure trained_models/ directory exists
- Check model file paths in config.yaml
- Verify sufficient memory available

### No Alerts Appearing
- Generate test traffic: `sudo venv/bin/python generate_anomalies.py --target 127.0.0.1 --syn-flood`
- Check logs for errors
- Verify ML models are loaded correctly

## Performance Tuning

### For High Traffic Environments
1. Increase worker processes:
   ```bash
   uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

2. Adjust packet analysis threshold in `src/network/traffic_analyzer.py`:
   ```python
   if len(flow['packets']) % 20 == 0:  # Analyze every 20 packets instead of 10
   ```

3. Use production ASGI server:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
   ```

## Backup and Maintenance

### Backup Important Data
```bash
# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Backup configuration
cp config.yaml config.yaml.bak
cp .env .env.bak
```

### Update the System
```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker-compose build --no-cache
docker-compose up -d
```

## Support

For issues and questions:
- Check logs: `logs/app.log`
- Review documentation: `README.md`, `ENHANCEMENTS.md`
- Check GitHub issues: [Repository Issues](repository-url/issues)
