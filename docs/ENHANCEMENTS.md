# System Enhancements Documentation

This document describes the new features added to the IDS & IoT Security System.

## Overview

All recommended enhancements have been implemented to improve threat detection, notification, response, and monitoring capabilities.

---

## 1. Email/SMS Notification System

**Location:** [src/utils/notification_service.py](src/utils/notification_service.py)

### Features
- **Email Alerts:** Send HTML-formatted email notifications for security threats
- **SMS Alerts:** Send SMS notifications via Twilio for critical threats
- **Summary Reports:** Automated periodic reports with statistics
- **Severity Filtering:** Only send notifications for threats above a specified severity threshold

### Configuration

Edit [config.yaml](config.yaml):

```yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your-email@gmail.com"
    recipients:
      - "security-team@example.com"
  sms:
    enabled: true
    from_number: "+1234567890"
    recipients:
      - "+1234567890"
```

### Environment Variables (Recommended)
```bash
export EMAIL_PASSWORD="your-email-password"
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
```

### Usage
Notifications are sent automatically when threats are detected. The system checks severity levels and only sends notifications for critical threats (configurable).

---

## 2. Alert Dashboard Filtering

**Location:** [src/api/endpoints.py](src/api/endpoints.py)

### API Endpoints

#### Get Filtered Alerts
```http
GET /api/alerts?severity=high&acknowledged=false&limit=50
```

**Query Parameters:**
- `severity`: Filter by severity (low, medium, high)
- `threat`: Filter by threat type
- `acknowledged`: Filter by acknowledgment status (true/false)
- `status`: Filter by status (new, investigating, resolved, false_positive)
- `limit`: Maximum number of alerts to return

**Response:**
```json
{
  "alerts": [...],
  "total": 25,
  "filters_applied": {
    "severity": "high",
    "acknowledged": false
  }
}
```

#### Get Alert Details
```http
GET /api/alerts/{alert_id}
```

---

## 3. Threat Statistics and Reporting

**Location:** [src/utils/statistics_tracker.py](src/utils/statistics_tracker.py)

### Features
- Real-time statistics tracking
- Hourly, daily, and weekly summaries
- Top threats and source IPs
- Alert trends over time

### API Endpoints

#### Get Statistics Summary
```http
GET /api/statistics/summary?period=daily
```

**Periods:** `hourly`, `daily`, `weekly`, `all`

**Response:**
```json
{
  "period": "Last 24 Hours",
  "total_alerts": 145,
  "high_severity": 12,
  "medium_severity": 45,
  "low_severity": 88,
  "top_threats": {
    "DDoS": 45,
    "Port Scan": 30,
    "Brute Force": 15
  },
  "top_sources": {
    "192.168.1.100": 20,
    "10.0.0.50": 15
  }
}
```

#### Get Real-time Stats
```http
GET /api/statistics/realtime
```

#### Get Alerts by Severity/Status
```http
GET /api/statistics/by-severity
GET /api/statistics/by-status
```

### Data Persistence
Statistics are automatically saved to `logs/statistics.json` and persist across restarts.

---

## 4. Enhanced Automated Response System

**Location:** [src/utils/response_actions.py](src/utils/response_actions.py)

### Features
- **Automatic IP Blocking:** Block malicious IPs using iptables
- **Rate Limiting:** Apply rate limits to suspicious sources
- **Temporary vs Permanent Blocks:** Configurable block durations
- **IP Whitelisting:** Prevent accidental blocking of trusted IPs
- **Action History:** Track all automated actions taken

### Configuration

Edit [config.yaml](config.yaml):

```yaml
response_actions:
  enabled: true
  auto_block_high_severity: true
  auto_block_medium_severity: false
  rate_limit_threshold: 100  # packets per second
  temp_block_duration: 3600  # seconds (1 hour)
```

### Response Actions by Severity

| Severity | Automatic Action |
|----------|-----------------|
| High     | Immediate IP block (temporary) |
| Medium   | Rate limiting (10 packets/sec) |
| Low      | Monitor only (no action) |

### API Endpoints

#### Block IP Manually
```http
POST /api/response/block-ip
Content-Type: application/json

{
  "ip_address": "192.168.1.100",
  "reason": "manual_block",
  "permanent": false
}
```

#### Unblock IP
```http
POST /api/response/unblock-ip/192.168.1.100
```

#### Get Blocked IPs
```http
GET /api/response/blocked-ips
```

#### Get Action History
```http
GET /api/response/action-history?limit=100
```

### Automatic Expiration
Temporary blocks automatically expire after the configured duration. The system periodically checks and unblocks expired IPs.

---

## 5. Alert Acknowledgment System

**Location:** [src/utils/alert_manager.py](src/utils/alert_manager.py)

### Features
- Track which alerts have been reviewed
- Add notes to alerts
- Update alert status (new, investigating, resolved, false_positive)
- Track who acknowledged each alert and when
- Filter alerts by acknowledgment status

### API Endpoints

#### Acknowledge Alert
```http
POST /api/alerts/{alert_id}/acknowledge
Content-Type: application/json

{
  "user": "admin",
  "notes": "Investigated - legitimate traffic from internal scanner"
}
```

#### Update Alert Status
```http
POST /api/alerts/{alert_id}/status
Content-Type: application/json

{
  "status": "resolved",
  "notes": "Blocked source IP, monitoring for recurrence"
}
```

**Valid Statuses:**
- `new` - Alert not yet reviewed
- `investigating` - Under investigation
- `resolved` - Issue resolved
- `false_positive` - False alarm

#### Get Unacknowledged Count
```http
GET /api/alerts/stats/unacknowledged
```

**Response:**
```json
{
  "unacknowledged_count": 23
}
```

### Data Persistence
Alert tracking data is automatically saved to `logs/alert_tracking.json`.

---

## Integration in Traffic Analyzer

All enhancements are integrated into [src/network/traffic_analyzer.py](src/network/traffic_analyzer.py):

```python
# When a threat is detected:
1. Alert is added to alert_manager (with unique ID)
2. Statistics are recorded in statistics_tracker
3. Notifications are sent (if configured and severity threshold met)
4. Automated response actions are taken (based on severity)
5. Alert is logged to file and WebSocket
```

---

## Complete API Documentation

### Base URL
```
http://localhost:8000/api
```

### Alert Endpoints
- `GET /alerts` - Get filtered alerts
- `GET /alerts/{alert_id}` - Get alert details
- `POST /alerts/{alert_id}/acknowledge` - Acknowledge alert
- `POST /alerts/{alert_id}/status` - Update alert status
- `GET /alerts/stats/unacknowledged` - Get unacknowledged count

### Statistics Endpoints
- `GET /statistics/summary` - Get statistics summary
- `GET /statistics/realtime` - Get real-time stats
- `GET /statistics/by-severity` - Get alerts by severity
- `GET /statistics/by-status` - Get alerts by status

### Response Action Endpoints
- `POST /response/block-ip` - Block an IP
- `POST /response/unblock-ip/{ip}` - Unblock an IP
- `GET /response/blocked-ips` - Get blocked IPs
- `GET /response/action-history` - Get action history

### Flow Endpoints
- `GET /flows` - Get current network flows

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure System
Edit `config.yaml` to enable notifications and configure response actions.

### 3. Set Environment Variables (Optional but Recommended)
```bash
export EMAIL_PASSWORD="your-password"
export TWILIO_ACCOUNT_SID="your-sid"
export TWILIO_AUTH_TOKEN="your-token"
```

### 4. Run the System
```bash
# Requires root for packet capture
sudo uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

---

## Testing

### Test Notification System
```python
from src.utils.notification_service import NotificationService

config = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'test@example.com',
        'password': 'password',
        'recipients': ['recipient@example.com']
    }
}

service = NotificationService(config)
alert = {
    'threat': 'DDoS',
    'severity': 'high',
    'src': '192.168.1.100',
    'dst': '10.0.0.1',
    'context': 'Test alert'
}
service.send_alert(alert)
```

### Test API Endpoints
```bash
# Get all high-severity alerts
curl "http://localhost:8000/api/alerts?severity=high"

# Get statistics summary
curl "http://localhost:8000/api/statistics/summary?period=daily"

# Block an IP
curl -X POST "http://localhost:8000/api/response/block-ip" \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.1.100", "reason": "test_block"}'
```

---

## Logging and Monitoring

### Log Files
- `logs/alerts.jsonl` - All security alerts (JSON format)
- `logs/statistics.json` - Aggregated statistics
- `logs/alert_tracking.json` - Alert acknowledgment data
- `logs/app.log` - Application logs

### WebSocket Endpoints
- `ws://localhost:8000/ws/alerts` - Real-time alert stream
- `ws://localhost:8000/ws/flows` - Real-time network flows

---

## Security Considerations

1. **Email Credentials:** Use environment variables, never commit passwords to version control
2. **Root Privileges:** Required for packet capture and iptables manipulation
3. **API Security:** Consider adding authentication for production deployments
4. **Rate Limiting:** Configure appropriate thresholds to avoid false positives
5. **Whitelisting:** Always whitelist trusted IPs before enabling auto-blocking

---

## Troubleshooting

### Notifications Not Sending
- Check `config.yaml` has `enabled: true`
- Verify environment variables are set correctly
- Check application logs for error messages
- For Gmail, enable "Less secure app access" or use App Passwords

### Automated Responses Not Working
- Ensure the application is running as root
- Check `response_actions.enabled: true` in config
- Verify iptables is installed and accessible
- Check action history endpoint for error details

### Statistics Not Updating
- Statistics are updated only when threats are detected
- Check that traffic analyzer is running
- Verify `logs/statistics.json` is being updated

---

## Future Enhancements

Potential additions for future versions:
- Dashboard UI with filtering controls
- Email report scheduling (daily/weekly automatic reports)
- Integration with SIEM systems
- Machine learning-based response tuning
- Advanced threat correlation
- Multi-tenancy support
