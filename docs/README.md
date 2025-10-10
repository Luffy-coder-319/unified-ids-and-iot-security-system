# Unified IDS and IoT Security System

This project implements a unified Intrusion Detection System (IDS) and IoT security system using machine learning for real-time threat detection.

## ✨ Key Features

### Core Capabilities
- **Real-time packet sniffing and analysis** - Live network traffic monitoring
- **AI-powered threat detection** - Dual ML models (RandomForest + Autoencoder)
- **IoT device profiling** - Automatic device behavior tracking
- **Web-based dashboard** - Real-time visualization of alerts and flows
- **REST API** - Full integration capabilities

### 🆕 Enhanced Features
- **Email/SMS Notifications** - Instant alerts for critical threats via email and SMS
- **Advanced Alert Management** - Acknowledge, track, and manage security alerts
- **Threat Statistics & Reporting** - Comprehensive analytics and summaries (hourly/daily/weekly)
- **Automated Response System** - Intelligent IP blocking, rate limiting, and threat mitigation
- **Alert Filtering** - Filter by severity, type, status, and acknowledgment

See [ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed documentation of all enhanced features.

## 🚀 Quick Start

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd unified-ids-and-iot-security-system
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure the system
```bash
# Copy and edit configuration
cp .env.example .env
# Edit config.yaml to enable features
nano config.yaml
```

5. Run tests
```bash
python test_enhancements.py
```

### Running the System

**Development Mode:**
```bash
uvicorn src.api.main:app --reload
```

**Production Mode (requires root):**
```bash
sudo uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**With Docker:**
```bash
docker build -t ids-system .
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN -p 8000:8000 ids-system
```

## 📊 API Endpoints

### Core Endpoints
- `GET /api/alerts` - Get filtered alerts
- `GET /api/statistics/summary` - Get threat statistics
- `GET /api/flows` - Get network flows
- `WebSocket /ws/alerts` - Real-time alert stream
- `WebSocket /ws/flows` - Real-time flow stream

### Alert Management
- `GET /api/alerts/{id}` - Get alert details
- `POST /api/alerts/{id}/acknowledge` - Acknowledge alert
- `POST /api/alerts/{id}/status` - Update alert status
- `GET /api/alerts/stats/unacknowledged` - Get unacknowledged count

### Response Actions
- `POST /api/response/block-ip` - Block IP address
- `POST /api/response/unblock-ip/{ip}` - Unblock IP
- `GET /api/response/blocked-ips` - Get blocked IPs
- `GET /api/response/action-history` - Get action history

### Statistics
- `GET /api/statistics/realtime` - Real-time stats
- `GET /api/statistics/by-severity` - Alerts by severity
- `GET /api/statistics/by-status` - Alerts by status

Full API documentation: [ENHANCEMENTS.md](ENHANCEMENTS.md)

## ⚙️ Configuration

### Basic Configuration (config.yaml)
```yaml
notifications:
  email:
    enabled: true  # Enable email alerts
  sms:
    enabled: true  # Enable SMS alerts

response_actions:
  enabled: true
  auto_block_high_severity: true  # Auto-block high threats
  temp_block_duration: 3600  # 1 hour
```

### Environment Variables (.env)
```bash
EMAIL_PASSWORD=your-email-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

See [ENHANCEMENTS.md](ENHANCEMENTS.md) for detailed configuration options.
