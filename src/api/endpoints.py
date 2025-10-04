from fastapi import APIRouter, HTTPException
from src.network.traffic_analyzer import alerts, flows

router = APIRouter

@router.get("/alerts")
def get_alerts():
    return alerts

@router.get("/flows")
def get_flows():
    return [{"key": k, "pkt_count": len(v['packets'])} for k, v in flows.items()]