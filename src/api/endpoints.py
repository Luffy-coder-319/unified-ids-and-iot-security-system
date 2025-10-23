from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from src.network.traffic_analyzer import (
    alerts, flows, statistics_tracker, alert_manager,
    response_manager, notification_service,
    detection_mode, detection_config
)
from src.network.packet_sniffer import get_network_interfaces, get_active_interface
from src.iot_security.device_detector import iot_detector
import src.network.traffic_analyzer as traffic_analyzer

router = APIRouter()

# Request models
class AcknowledgeAlertRequest(BaseModel):
    alert_id: int
    user: str = "admin"
    notes: str = ""

class UpdateAlertStatusRequest(BaseModel):
    alert_id: int
    status: str
    notes: str = ""

class BlockIPRequest(BaseModel):
    ip_address: str
    reason: str = "manual_block"
    permanent: bool = False

class DetectionModeRequest(BaseModel):
    mode: str  # 'threshold' or 'pure_ml'


# Alert endpoints
@router.get("/alerts")
def get_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high)"),
    threat: Optional[str] = Query(None, description="Filter by threat type"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(100, description="Maximum number of alerts to return")
):
    """Get alerts with optional filtering."""
    filters = {}
    if severity:
        filters['severity'] = severity.lower()
    if threat:
        filters['threat'] = threat
    if acknowledged is not None:
        filters['acknowledged'] = acknowledged
    if status:
        filters['status'] = status

    filtered_alerts = alert_manager.get_alerts(filters=filters, limit=limit)
    return {
        "alerts": filtered_alerts,
        "total": len(filtered_alerts),
        "filters_applied": filters
    }

@router.get("/alerts/{alert_id}")
def get_alert_details(alert_id: int):
    """Get details of a specific alert."""
    alert = alert_manager.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, request: AcknowledgeAlertRequest):
    """Acknowledge an alert."""
    success = alert_manager.acknowledge_alert(
        alert_id=alert_id,
        user=request.user,
        notes=request.notes
    )
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert acknowledged", "alert_id": alert_id}

@router.post("/alerts/{alert_id}/status")
def update_alert_status(alert_id: int, request: UpdateAlertStatusRequest):
    """Update alert status."""
    success = alert_manager.update_alert_status(
        alert_id=alert_id,
        status=request.status,
        notes=request.notes
    )
    if not success:
        raise HTTPException(status_code=400, detail="Invalid status or alert not found")
    return {"message": "Alert status updated", "alert_id": alert_id, "status": request.status}

@router.get("/alerts/stats/unacknowledged")
def get_unacknowledged_count():
    """Get count of unacknowledged alerts."""
    return {"unacknowledged_count": alert_manager.get_unacknowledged_count()}

@router.post("/alerts/clear")
def clear_alerts():
    """Clear all alerts (for testing purposes)."""
    try:
        # Clear the alerts list
        alerts.clear()
        # Clear alert manager
        alert_manager.alerts.clear()
        return {"message": "All alerts cleared", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear alerts: {str(e)}")


# Statistics endpoints
@router.get("/statistics/summary")
def get_statistics_summary(period: str = Query("all", description="Period: hourly, daily, weekly, all")):
    """Get threat statistics summary."""
    return statistics_tracker.get_summary(period=period)

@router.get("/statistics/realtime")
def get_realtime_stats():
    """Get real-time statistics for dashboard."""
    return statistics_tracker.get_real_time_stats()

@router.get("/statistics/by-severity")
def get_alerts_by_severity():
    """Get alert counts by severity."""
    return alert_manager.get_alerts_by_severity()

@router.get("/statistics/by-status")
def get_alerts_by_status():
    """Get alert counts by status."""
    return alert_manager.get_alerts_by_status()


# Flow endpoints
@router.get("/flows")
def get_flows():
    """Get current network flows."""
    return [{"key": k, "pkt_count": len(v['packets'])} for k, v in flows.items()]


# Response action endpoints
@router.post("/response/block-ip")
def block_ip(request: BlockIPRequest):
    """Block an IP address."""
    if not response_manager:
        raise HTTPException(status_code=503, detail="Response manager not initialized")

    success = response_manager.block_ip(
        ip_address=request.ip_address,
        reason=request.reason,
        permanent=request.permanent
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to block IP")
    return {"message": f"IP {request.ip_address} blocked successfully"}

@router.post("/response/unblock-ip/{ip_address}")
def unblock_ip(ip_address: str):
    """Unblock an IP address."""
    if not response_manager:
        raise HTTPException(status_code=503, detail="Response manager not initialized")

    success = response_manager.unblock_ip(ip_address)
    if not success:
        raise HTTPException(status_code=404, detail="IP not currently blocked or failed to unblock")
    return {"message": f"IP {ip_address} unblocked successfully"}

@router.get("/response/blocked-ips")
def get_blocked_ips():
    """Get list of currently blocked IPs."""
    if not response_manager:
        return {"blocked_ips": {}}
    return {"blocked_ips": response_manager.get_blocked_ips()}

@router.get("/response/action-history")
def get_action_history(limit: int = Query(100, description="Number of actions to return")):
    """Get history of automated response actions."""
    if not response_manager:
        return {"actions": []}
    return {"actions": response_manager.get_action_history(limit=limit)}


# Network interface endpoints
@router.get("/network/interfaces")
def get_interfaces():
    """Get information about all network interfaces."""
    try:
        interfaces = get_network_interfaces()
        active_interface = get_active_interface()
        return {
            "interfaces": interfaces,
            "active_interface": active_interface,
            "total": len(interfaces)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network interfaces: {str(e)}")

@router.get("/network/status")
def get_network_status():
    """Get current network monitoring status."""
    try:
        interfaces = get_network_interfaces()
        active_interface = get_active_interface()

        # Filter out loopback to show only external interfaces
        external_interfaces = [iface for iface in interfaces if not iface['is_loopback']]

        return {
            "monitoring_interface": active_interface,
            "external_ips": [iface['ip'] for iface in external_interfaces],
            "interface_count": len(interfaces),
            "external_interface_count": len(external_interfaces),
            "details": external_interfaces
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get network status: {str(e)}")



# IoT Device Detection endpoints
@router.get("/iot/devices")
def get_iot_devices():
    """Get all detected devices (IoT and non-IoT)."""
    try:
        all_devices = iot_detector.get_all_devices()

        # Convert sets to lists for JSON serialization
        for device in all_devices:
            if 'ports_used' in device:
                device['ports_used'] = list(device['ports_used'])
            if 'protocols_seen' in device:
                device['protocols_seen'] = list(device['protocols_seen'])
            # Convert datetime to string
            if 'first_seen' in device:
                device['first_seen'] = device['first_seen'].isoformat()
            if 'last_seen' in device:
                device['last_seen'] = device['last_seen'].isoformat()

        return {
            "devices": all_devices,
            "total": len(all_devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")

@router.get("/iot/summary")
def get_iot_summary():
    """Get summary of IoT device detection."""
    try:
        summary = iot_detector.get_device_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get IoT summary: {str(e)}")

@router.get("/iot/devices/{ip_address}")
def get_device_details(ip_address: str):
    """Get details of a specific device by IP address."""
    try:
        device = iot_detector.get_device_info(ip_address=ip_address)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Convert sets to lists for JSON serialization
        if 'ports_used' in device:
            device['ports_used'] = list(device['ports_used'])
        if 'protocols_seen' in device:
            device['protocols_seen'] = list(device['protocols_seen'])
        # Convert datetime to string
        if 'first_seen' in device:
            device['first_seen'] = device['first_seen'].isoformat()
        if 'last_seen' in device:
            device['last_seen'] = device['last_seen'].isoformat()

        return device
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device details: {str(e)}")


# Detection Mode endpoints
@router.get("/detection/mode")
def get_detection_mode():
    """Get current detection mode and configuration."""
    return {
        "mode": traffic_analyzer.detection_mode,
        "config": traffic_analyzer.detection_config,
        "available_modes": ["threshold", "pure_ml"],
        "description": {
            "threshold": "Multi-layer filtering with confidence thresholds (recommended for production)",
            "pure_ml": "Pure ML detection without filtering (best for testing and validation)"
        }
    }

@router.post("/detection/mode")
def set_detection_mode(request: DetectionModeRequest):
    """Set detection mode."""
    if request.mode not in ["threshold", "pure_ml"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be 'threshold' or 'pure_ml'")

    traffic_analyzer.detection_mode = request.mode
    return {
        "message": f"Detection mode set to '{request.mode}'",
        "mode": traffic_analyzer.detection_mode,
        "success": True
    }
