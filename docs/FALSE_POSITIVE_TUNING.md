# False Positive Tuning Guide

## Issue: Normal Traffic Triggering Alerts

If legitimate applications (gaming, streaming, VPN, P2P) are triggering alerts, you need to tune the detection system.

## Quick Fixes

### Option 1: Increase Confidence Threshold (Recommended)

Edit `src/network/traffic_analyzer.py`:

```python
# Around line 173
min_confidence = detection_config.get('confidence_threshold', 0.98)  # Change from 0.95 to 0.98
```

**Effect**: Only alerts when model is 98%+ confident (instead of 95%+)

### Option 2: Increase Packet Threshold

```python
# Around line 179
min_packet_threshold = detection_config.get('min_packet_threshold', 500)  # Change from 100 to 500
```

**Effect**: Only alerts on very sustained connections (500+ packets instead of 100+)

### Option 3: Whitelist Specific IPs

Add the legitimate IP to the cloud providers whitelist:

```python
# Around line 184, add to cloud_providers set:
cloud_providers = {
    # ... existing entries ...
    '185.159.',  # Add your legitimate service
}
```

### Option 4: Whitelist Specific Ports

```python
# Around line 254, add to legitimate_ports:
legitimate_ports = {80, 443, 53, 8080, 8443, 3000, 5000, 8000, 5815}  # Add 5815
```

### Option 5: Ignore Specific Attack Types

Add attack type filtering before the alert:

```python
# Around line 260, add:
ignored_attack_types = {
    'Mirai-greip_flood',  # If your traffic is being misclassified as Mirai
    'DDoS-ICMP_Fragmentation',  # If normal fragmentation is being flagged
}

is_ignored_attack = threat in ignored_attack_types

# Then in the should_alert condition (line 267):
should_alert = (
    is_threat and
    has_high_confidence and
    has_significant_traffic and
    not is_cloud_provider and
    not is_local_traffic and
    not (is_legitimate_port and pkt_count < 200) and
    not is_ignored_attack  # Add this line
)
```

## Recommended Combination for Home/Personal Networks

For networks with gaming, streaming, VPN, or P2P applications, use these settings:

```python
# More lenient configuration for home networks
detection_config = {
    'confidence_threshold': 0.98,  # Very high confidence required
    'min_packet_threshold': 500    # Long-lived connections only
}

# Add common gaming/streaming ports
legitimate_ports = {
    80, 443, 53, 8080, 8443, 3000, 5000, 8000,
    5815, 3074, 27015, 25565,  # Gaming ports
    1935, 8935,  # Streaming
}

# Whitelist attack types that are commonly false positives
ignored_attack_types = {
    'Mirai-greip_flood',  # Often triggered by gaming traffic
    'DDoS-ICMP_Fragmentation',  # Often triggered by normal fragmentation
}
```

## Step-by-Step Tuning Process

### Step 1: Identify What's Being Flagged

When you see an alert, identify the application:

```bash
# Windows
netstat -ano | findstr "185.159.159.148"
netstat -ano | findstr "5815"
tasklist | findstr <PID>

# Linux/Mac
netstat -tunapl | grep 185.159.159.148
lsof -i :5815
```

### Step 2: Determine if Legitimate

If the application is:
- ✅ Gaming client (Steam, Epic, Xbox, PlayStation)
- ✅ Video streaming (Netflix, YouTube, Twitch)
- ✅ VPN client
- ✅ P2P application (BitTorrent, etc.)
- ✅ Video conferencing (Zoom, Teams, Discord)
- ✅ Cloud backup service

Then it's a **false positive** and should be whitelisted.

### Step 3: Choose Tuning Method

| Application Type | Recommended Fix |
|-----------------|-----------------|
| **Known gaming/streaming service** | Whitelist the IP range or port |
| **VPN/Proxy** | Whitelist the IP |
| **Multiple legitimate apps** | Increase confidence threshold to 98-99% |
| **P2P (torrents, etc.)** | Whitelist the port and increase packet threshold |
| **General home network** | Increase both confidence (98%) and packets (500) |

### Step 4: Apply Changes

1. Edit `src/network/traffic_analyzer.py`
2. Restart the monitoring system
3. Monitor for 1-2 hours
4. Adjust further if needed

## Understanding Model Behavior

The retrained models were trained on **network attack datasets** which may not include:
- Modern gaming traffic patterns
- High-bitrate streaming
- VPN encrypted traffic
- P2P protocols

This can cause **pattern confusion** where:
- Gaming → Classified as DDoS (high packet rate)
- VPN → Classified as Mirai (encrypted bulk transfer)
- Streaming → Classified as flood attack (sustained high bandwidth)

## Advanced: Per-Application Whitelisting

Create a whitelist based on your specific applications:

```python
# Add after line 210 in traffic_analyzer.py

# Application-specific whitelist
app_whitelist = {
    # Gaming platforms
    ('185.159.159.0/24', 5815): 'Gaming Server',
    # VPN services
    ('10.8.0.0/24', None): 'VPN Network',
    # Streaming services
    (None, 1935): 'RTMP Streaming',
}

def is_whitelisted_app(src_ip, dst_ip, port):
    """Check if connection matches known legitimate application."""
    for (ip_pattern, app_port), app_name in app_whitelist.items():
        if app_port and port == app_port:
            return True, app_name
        if ip_pattern:
            # Check if IP matches pattern (simplified)
            if src_ip.startswith(ip_pattern.split('/')[0][:10]) or \
               dst_ip.startswith(ip_pattern.split('/')[0][:10]):
                return True, app_name
    return False, None

# Use in filtering logic:
is_whitelisted, app_name = is_whitelisted_app(key[0], key[1], dst_port)
if is_whitelisted:
    print(f"[WHITELIST] {key[0]}->{key[1]}:{dst_port} | App:{app_name}")
    continue  # Skip alert
```

## Quick Temporary Fix

To immediately stop these specific alerts while you investigate:

```python
# Add near line 276, before should_alert check:
if '185.159.159.148' in [key[0], key[1]]:
    print(f"[WHITELIST] Ignoring traffic to/from 185.159.159.148 (known legitimate service)")
    continue
```

## Recommended Settings by Environment

### Corporate/Enterprise Network
```python
confidence_threshold = 0.95  # Keep strict
min_packet_threshold = 100   # Keep strict
# Use extensive whitelisting for known services
```

### Home Network (Gaming/Streaming)
```python
confidence_threshold = 0.98  # More lenient
min_packet_threshold = 500   # More lenient
# Whitelist gaming/streaming ports and IPs
```

### Research/Lab Network
```python
detection_mode = 'pure_ml'  # Log everything
# Manual review of all detections
```

### IoT Network
```python
confidence_threshold = 0.90  # More sensitive
min_packet_threshold = 50    # More sensitive
# IoT devices shouldn't have high traffic
```

## Testing Your Changes

After applying changes:

1. **Monitor debug output**: Should see `[WHITELIST]` or `[FILTER]` messages
2. **Check alert count**: Should decrease significantly
3. **Verify legitimate traffic**: Make sure normal apps work without alerts
4. **Test with attack**: Verify real attacks still generate alerts

## When to Use Pure ML Mode

Use `detection_mode = 'pure_ml'` temporarily to:
- See ALL model predictions
- Understand your network baseline
- Identify patterns to whitelist
- Then switch back to 'threshold' mode with proper tuning

## Summary

For your current situation with normal traffic being flagged:

**Immediate Action**:
```python
# Option A: Quick whitelist (line ~210)
cloud_providers.add('185.159.')

# Option B: Increase thresholds (lines ~173, 179)
min_confidence = 0.98
min_packet_threshold = 500

# Option C: Ignore specific attacks (line ~260)
ignored_attack_types = {'Mirai-greip_flood', 'DDoS-ICMP_Fragmentation'}
```

Choose the option that best fits your use case!
