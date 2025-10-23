# Attack Testing Guide

This guide explains how to test the IDS system with simulated attacks and why you might not see alerts in certain scenarios.

## Understanding Detection Modes

The system has two detection modes:

### 1. Threshold Mode (Default - Production)
- **Purpose**: Minimize false positives in real-world environments
- **How it works**: Multi-layer filtering with strict thresholds
- **Best for**: Production use, home networks, enterprise environments

**Filtering Layers:**
1. **Confidence Threshold**: ≥98% confidence required
2. **Packet Threshold**: ≥500 packets required (sustained traffic)
3. **Cloud Provider Whitelist**: Ignores traffic to/from known cloud services (AWS, Azure, Google, Cloudflare, etc.)
4. **Private Network Filtering**: Filters out local/private IP communication (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
5. **Legitimate Port Whitelist**: Reduces sensitivity for common ports (80, 443, 53, etc.)
6. **Attack Type Filtering**: Ignores commonly misclassified attack types
7. **Adaptive Baseline Learning**: Learns normal network patterns over time

### 2. Pure ML Mode (Testing)
- **Purpose**: See raw ML model predictions without filtering
- **How it works**: Trusts ML model completely, no thresholds or filtering
- **Best for**: Testing, validation, research, development

## Why You Might Not See Alerts

### Common Reasons:

1. **Testing with Private IP Addresses**
   - **Problem**: The target IP (e.g., 192.168.56.1) is a private network address
   - **Why**: Layer 4 filtering blocks private network traffic to prevent false positives
   - **Solution**: Use the test mode script or switch to pure ML mode

2. **Insufficient Packet Count**
   - **Problem**: Not enough packets generated (threshold mode requires ≥500 packets)
   - **Why**: Prevents alerting on brief, normal connections
   - **Solution**: Increase attack packet count or use pure ML mode

3. **Legitimate Port Usage**
   - **Problem**: Attacking common ports like 80 (HTTP) or 443 (HTTPS)
   - **Why**: System is more lenient with standard web traffic
   - **Solution**: Target non-standard ports or use pure ML mode

4. **Network Adapter Not Capturing**
   - **Problem**: Packets aren't being captured by the monitoring interface
   - **Why**: Wrong network adapter selected or permission issues
   - **Solution**: Check server logs, verify interface in config.yaml

## Testing Scripts

### For External/Real Attacks: `test_external_attacks.ps1`
```powershell
cd scripts
.\test_external_attacks.ps1
```
- **Best for**: Testing with external IP addresses
- **Requires**: Administrator privileges
- **Mode**: Uses current detection mode (threshold by default)
- **Target**: Your external network IP

### For Local/Test Attacks: `test_local_attacks.ps1`
```powershell
cd scripts
.\test_local_attacks.ps1
```
- **Best for**: Testing with local/private IP addresses
- **Requires**: Administrator privileges
- **Mode**: Automatically switches to pure ML mode
- **Target**: Your local network IP
- **Auto-restoration**: Switches back to threshold mode when done

## Manual Mode Switching

You can manually switch detection modes via the API:

### Enable Pure ML Mode (for testing)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode" `
  -Method POST `
  -Body '{"mode":"pure_ml"}' `
  -ContentType "application/json"
```

### Enable Threshold Mode (for production)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode" `
  -Method POST `
  -Body '{"mode":"threshold"}' `
  -ContentType "application/json"
```

### Check Current Mode
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode" | ConvertFrom-Json
```

## Attack Simulation Options

The test scripts support multiple attack types:

### 1. SYN Flood (DDoS)
```powershell
python run_attack.py --target IP --syn-flood --count 300 --rate 200
```
- Simulates TCP SYN flood attack
- High packet rate to overwhelm target
- Commonly used in DDoS attacks

### 2. UDP Flood
```powershell
python run_attack.py --target IP --udp-flood --count 300 --rate 200
```
- Simulates UDP flood attack
- Large payload packets
- Bandwidth exhaustion attack

### 3. Port Scan
```powershell
python run_attack.py --target IP --port-scan --ports 75-100
```
- Simulates reconnaissance/scanning
- Tests multiple ports sequentially
- Detects open/closed ports

### 4. All Attacks (Comprehensive)
```powershell
python run_attack.py --target IP --syn-flood --udp-flood --count 250
```
- Runs multiple attack types
- Best for comprehensive testing
- Validates detection across attack categories

## Troubleshooting

### No Alerts Generated

1. **Check Detection Mode**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/api/detection/mode"
   ```

2. **Check Server Logs**
   - Look for `[FILTER]` messages in server terminal
   - Shows why attacks were filtered
   - Example: `[FILTER] ... Local:True` means private network filtering

3. **Verify Packet Capture**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:8000/api/network/status"
   ```
   - Check `monitoring_interface` matches your active adapter

4. **Check Config**
   - Review `config.yaml` settings
   - Verify `confidence_threshold` (default: 0.98)
   - Check `min_packet_threshold` (default: 500)
   - Confirm `filter_private_networks` setting

### Server Not Capturing Packets

1. **Administrator Privileges**: Packet capture requires admin rights
2. **Correct Interface**: Verify config.yaml has the right network adapter
3. **Firewall**: Check Windows Firewall isn't blocking packet capture
4. **Dependencies**: Ensure Scapy and Npcap are properly installed

## Best Practices

### For Testing
1. Use `test_local_attacks.ps1` for quick local tests
2. Enable pure ML mode to see all detections
3. Start with SYN flood (most reliable)
4. Monitor server terminal for debug output

### For Production
1. Keep threshold mode enabled
2. Allow adaptive baseline to learn (1 hour learning period)
3. Monitor false positive rate
4. Adjust thresholds in config.yaml if needed
5. Review and acknowledge alerts regularly

## API Endpoints for Testing

- **Clear Alerts**: `POST /api/alerts/clear`
- **Get Alerts**: `GET /api/alerts`
- **Detection Mode**: `GET/POST /api/detection/mode`
- **Network Status**: `GET /api/network/status`
- **Real-time Stats**: `GET /api/statistics/realtime`

## Expected Behavior

### Threshold Mode (Production)
- **Private Network Attack**: No alert (filtered by Layer 4)
- **Public IP SYN Flood (1000+ pkts)**: Alert (meets thresholds)
- **Cloud Service Traffic**: No alert (whitelisted)
- **Brief Connections (<500 pkts)**: No alert (below threshold)

### Pure ML Mode (Testing)
- **Any Malicious Traffic**: Alert (no filtering)
- **Private Network Attack**: Alert (no filtering)
- **Low Packet Count**: May still alert (no packet threshold)
- **Cloud Services**: May alert if ML detects anomaly

## Security Note

**IMPORTANT**: Only run attack simulations:
- On your own networks
- With proper authorization
- In isolated test environments
- For legitimate security testing purposes

Unauthorized attack simulation against external systems is illegal.

## Next Steps

1. Run `test_local_attacks.ps1` to verify system is working
2. Review generated alerts on dashboard
3. Switch to threshold mode for production use
4. Monitor and tune thresholds based on your network
5. Enable adaptive baseline learning for better accuracy
