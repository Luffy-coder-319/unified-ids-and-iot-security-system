from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from src.network.traffic_analyzer import (
    alerts, flows, statistics_tracker, alert_manager,
    response_manager, notification_service
)

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

