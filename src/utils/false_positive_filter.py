"""
False Positive Filter for legitimate traffic patterns.
Reduces false alarms on known-good traffic.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Known legitimate cloud/CDN services
LEGITIMATE_SERVICES = {
    # GitHub
    '140.82.113.0/24': 'GitHub',
    '192.30.252.0/22': 'GitHub',

    # Microsoft/Azure
    '20.0.0.0/8': 'Microsoft Azure',
    '13.64.0.0/11': 'Microsoft Azure',

    # Google/GCP
    '142.250.0.0/15': 'Google',
    '172.217.0.0/16': 'Google',
    '13.107.0.0/16': 'Microsoft',

    # Cloudflare
    '104.16.0.0/12': 'Cloudflare',
    '172.64.0.0/13': 'Cloudflare',

    # Amazon AWS
    '52.0.0.0/8': 'Amazon AWS',
    '54.0.0.0/8': 'Amazon AWS',
}

# Legitimate ports that should rarely be attack sources
LEGITIMATE_PORTS = {
    80,    # HTTP
    443,   # HTTPS
    53,    # DNS
    123,   # NTP
    22,    # SSH (when from known servers)
}

# Attack types that are commonly false positives on HTTPS traffic
#HTTPS_FALSE_POSITIVE_ATTACKS = {
#    'DDoS-RSTFINFlood',
#    'DDoS-ICMP_Fragmentation',
#    'DDoS-ACK_Fragmentation',
#    'Mirai-greip_flood',
#    'Mirai-greeth_flood',
#}


def is_ip_in_range(ip: str, cidr: str) -> bool:
    """Check if IP is in CIDR range."""
    try:
        from ipaddress import ip_address, ip_network
        return ip_address(ip) in ip_network(cidr, strict=False)
    except Exception:
        return False


def get_service_name(ip: str) -> Optional[str]:
    """Get service name for IP if it's a known legitimate service."""
    for cidr, service in LEGITIMATE_SERVICES.items():
        if is_ip_in_range(ip, cidr):
            return service
    return None


def is_likely_false_positive(
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    attack_type: str,
    confidence: float,
    packet_count: int = 0
) -> Dict[str, Any]:
    """
    Determine if a detected threat is likely a false positive.

    Args:
        src_ip: Source IP address
        dst_ip: Destination IP address
        src_port: Source port
        dst_port: Destination port
        attack_type: Detected attack type
        confidence: Detection confidence (0-1)
        packet_count: Number of packets in flow

    Returns:
        Dict with 'is_false_positive', 'reason', and 'action'
    """
    reasons = []

    # Check if source is a legitimate service
    src_service = get_service_name(src_ip)
    if src_service:
        reasons.append(f"Source is {src_service}")

    # Check if destination is a legitimate service
    dst_service = get_service_name(dst_ip)
    if dst_service:
        reasons.append(f"Destination is {dst_service}")

    # Check for HTTPS traffic to/from legitimate services
    if (dst_port == 443 or src_port == 443):
        if src_service or dst_service:
            if attack_type in HTTPS_FALSE_POSITIVE_ATTACKS:
                reasons.append("HTTPS traffic to/from known service")
                return {
                    'is_false_positive': True,
                    'reason': ' + '.join(reasons),
                    'action': 'suppress',
                    'service': src_service or dst_service
                }

    # Check for low packet count with high confidence attack
    # (Real attacks usually have more packets)
    if packet_count > 0 and packet_count < 30:
        if attack_type in HTTPS_FALSE_POSITIVE_ATTACKS:
            if confidence > 0.9:
                reasons.append(f"Low packet count ({packet_count}) for claimed attack")
                return {
                    'is_false_positive': True,
                    'reason': ' + '.join(reasons),
                    'action': 'reduce_severity',
                    'service': src_service or dst_service
                }

    # If we have reasons but not strong enough to suppress
    if reasons:
        return {
            'is_false_positive': False,
            'reason': ' + '.join(reasons),
            'action': 'flag_for_review',
            'service': src_service or dst_service
        }

    return {
        'is_false_positive': False,
        'reason': None,
        'action': 'none',
        'service': None
    }


def filter_alert(alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter an alert and return modified version or None to suppress.

    Args:
        alert: Alert dictionary with flow and threat info

    Returns:
        Modified alert dict or None to suppress
    """
    # Extract relevant info
    src_ip = alert.get('src_ip', '')
    dst_ip = alert.get('dst_ip', '')
    src_port = alert.get('src_port', 0)
    dst_port = alert.get('dst_port', 0)
    attack_type = alert.get('attack', 'Unknown')
    confidence = alert.get('confidence', 0.0)
    packet_count = alert.get('packet_count', 0)

    # Check for false positive
    fp_check = is_likely_false_positive(
        src_ip, dst_ip, src_port, dst_port,
        attack_type, confidence, packet_count
    )

    if fp_check['is_false_positive']:
        if fp_check['action'] == 'suppress':
            logger.info(
                f"Suppressing false positive: {src_ip}->{dst_ip}:{dst_port} "
                f"{attack_type} ({fp_check['reason']})"
            )
            return None

        elif fp_check['action'] == 'reduce_severity':
            # Downgrade severity but keep alert
            alert['severity'] = 'low'
            alert['confidence'] = confidence * 0.5  # Reduce confidence
            alert['notes'] = f"Possible false positive: {fp_check['reason']}"
            logger.info(
                f"Reduced severity: {src_ip}->{dst_ip}:{dst_port} "
                f"{attack_type} ({fp_check['reason']})"
            )

    elif fp_check['action'] == 'flag_for_review':
        # Add note but keep original severity
        alert['notes'] = f"Review: {fp_check['reason']}"
        if fp_check['service']:
            alert['service'] = fp_check['service']

    return alert
