"""
Adaptive Baseline Learning System

This module learns what's "normal" on your home network and adjusts detection thresholds accordingly.
It runs alongside the IDS and automatically adapts to your network patterns without manual retraining.

Key Features:
- Learns IP addresses, ports, and traffic patterns from your network
- Builds a whitelist of trusted IPs and common communication patterns
- Adjusts confidence thresholds based on flow characteristics
- Reduces false positives without requiring model retraining

Usage:
    from src.utils.adaptive_baseline import AdaptiveBaseline

    baseline = AdaptiveBaseline()

    # During detection:
    should_alert = baseline.evaluate_threat(
        src_ip='192.168.1.100',
        dst_ip='52.207.122.56',
        src_port=54321,
        dst_port=443,
        threat='DDoS-RSTFINFlood',
        confidence=0.96,
        packet_count=150
    )
"""

import os
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


class AdaptiveBaseline:
    """
    Adaptive baseline learning system that reduces false positives by
    learning normal network patterns.
    """

    def __init__(self, baseline_file='data/network_baseline.json', learning_period=3600):
        """
        Initialize adaptive baseline.

        Args:
            baseline_file: Path to save/load baseline data
            learning_period: Time in seconds to learn before enforcing rules (default: 1 hour)
        """
        self.baseline_file = Path(baseline_file)
        self.learning_period = learning_period
        self.start_time = time.time()

        # Learned patterns
        self.trusted_ips: Set[str] = set()
        self.common_flows: Dict[str, int] = defaultdict(int)  # (src_ip, dst_ip, dst_port) -> count
        self.port_usage: Dict[int, int] = defaultdict(int)  # port -> count
        self.ip_pair_confidence: Dict[str, float] = defaultdict(float)  # (src, dst) -> avg confidence

        # Statistics
        self.total_flows = 0
        self.benign_flows = 0
        self.threat_flows = 0

        # Load existing baseline if available
        self.load_baseline()

        logger.info(f"Adaptive baseline initialized (learning period: {learning_period}s)")

    def is_learning(self) -> bool:
        """Check if still in learning period."""
        return (time.time() - self.start_time) < self.learning_period

    def learn_flow(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        is_benign: bool = True
    ):
        """
        Learn from a flow.

        Args:
            src_ip: Source IP
            dst_ip: Destination IP
            src_port: Source port
            dst_port: Destination port
            is_benign: Whether this flow is benign (default: True for learning)
        """
        self.total_flows += 1

        if is_benign:
            self.benign_flows += 1

            # Learn IPs
            self.trusted_ips.add(src_ip)

            # Learn common flows
            flow_key = f"{src_ip}|{dst_ip}|{dst_port}"
            self.common_flows[flow_key] += 1

            # Learn port usage
            self.port_usage[dst_port] += 1

        else:
            self.threat_flows += 1

        # Auto-save every 100 flows
        if self.total_flows % 100 == 0:
            self.save_baseline()

    def is_trusted_ip(self, ip: str) -> bool:
        """Check if IP is in trusted list."""
        return ip in self.trusted_ips

    def is_common_flow(
        self,
        src_ip: str,
        dst_ip: str,
        dst_port: int,
        threshold: int = 10
    ) -> bool:
        """
        Check if this flow pattern is commonly seen.

        Args:
            src_ip: Source IP
            dst_ip: Destination IP
            dst_port: Destination port
            threshold: Minimum count to consider "common" (default: 10)

        Returns:
            True if this flow pattern is common
        """
        flow_key = f"{src_ip}|{dst_ip}|{dst_port}"
        return self.common_flows.get(flow_key, 0) >= threshold

    def is_common_port(self, port: int, threshold: int = 50) -> bool:
        """
        Check if port is commonly used.

        Args:
            port: Port number
            threshold: Minimum count to consider "common" (default: 50)

        Returns:
            True if port is commonly used
        """
        return self.port_usage.get(port, 0) >= threshold

    def evaluate_threat(
        self,
        src_ip: str,
        dst_ip: str,
        src_port: int,
        dst_port: int,
        threat: str,
        confidence: float,
        packet_count: int
    ) -> Dict[str, Any]:
        """
        Evaluate if a detected threat should trigger an alert.

        Args:
            src_ip: Source IP
            dst_ip: Destination IP
            src_port: Source port
            dst_port: Destination port
            threat: Detected threat type
            confidence: Model confidence (0-1)
            packet_count: Number of packets in flow

        Returns:
            Dict with:
                - should_alert: bool
                - reason: str (why alert was suppressed/kept)
                - adjusted_confidence: float (adjusted confidence score)
        """
        # During learning period, learn from everything
        if self.is_learning():
            # Assume most traffic during learning is benign
            # Learn from flows with low confidence or known benign patterns
            if confidence < 0.85 or threat == 'BenignTraffic':
                self.learn_flow(src_ip, dst_ip, src_port, dst_port, is_benign=True)

            return {
                'should_alert': True,  # During learning, trust the model
                'reason': 'learning_mode',
                'adjusted_confidence': confidence,
                'learning_progress': (time.time() - self.start_time) / self.learning_period
            }

        # After learning, apply adaptive filtering
        reasons = []
        confidence_adjustment = 0.0

        # Check if source is trusted
        if self.is_trusted_ip(src_ip):
            reasons.append('trusted_src_ip')
            confidence_adjustment -= 0.15  # Reduce confidence by 15%

        # Check if this is a common flow pattern
        if self.is_common_flow(src_ip, dst_ip, dst_port):
            reasons.append('common_flow_pattern')
            confidence_adjustment -= 0.20  # Reduce confidence by 20%

        # Check if port is commonly used
        if self.is_common_port(dst_port):
            reasons.append('common_port')
            confidence_adjustment -= 0.10  # Reduce confidence by 10%

        # Adjust confidence
        adjusted_confidence = max(0.0, confidence + confidence_adjustment)

        # Determine if should alert
        # Suppress alert if adjusted confidence drops below 0.85
        should_alert = adjusted_confidence >= 0.85

        # If suppressed, learn this as benign
        if not should_alert:
            self.learn_flow(src_ip, dst_ip, src_port, dst_port, is_benign=True)

        return {
            'should_alert': should_alert,
            'reason': ' + '.join(reasons) if reasons else 'no_baseline_match',
            'adjusted_confidence': adjusted_confidence,
            'confidence_adjustment': confidence_adjustment,
            'baseline_factors': reasons
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get baseline statistics."""
        learning_progress = min(1.0, (time.time() - self.start_time) / self.learning_period)

        return {
            'is_learning': self.is_learning(),
            'learning_progress': learning_progress,
            'total_flows': self.total_flows,
            'benign_flows': self.benign_flows,
            'threat_flows': self.threat_flows,
            'trusted_ips': len(self.trusted_ips),
            'common_flows': len(self.common_flows),
            'ports_learned': len(self.port_usage),
            'top_ports': dict(Counter(self.port_usage).most_common(10))
        }

    def save_baseline(self):
        """Save baseline to file."""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'start_time': self.start_time,
                'learning_period': self.learning_period,
                'trusted_ips': list(self.trusted_ips),
                'common_flows': dict(self.common_flows),
                'port_usage': dict(self.port_usage),
                'statistics': {
                    'total_flows': self.total_flows,
                    'benign_flows': self.benign_flows,
                    'threat_flows': self.threat_flows
                }
            }

            with open(self.baseline_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Baseline saved to {self.baseline_file}")

        except Exception as e:
            logger.error(f"Failed to save baseline: {e}")

    def load_baseline(self):
        """Load baseline from file if it exists."""
        if not self.baseline_file.exists():
            logger.info("No existing baseline found, starting fresh")
            return

        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)

            self.start_time = data.get('start_time', time.time())
            self.learning_period = data.get('learning_period', self.learning_period)
            self.trusted_ips = set(data.get('trusted_ips', []))
            self.common_flows = defaultdict(int, data.get('common_flows', {}))
            self.port_usage = defaultdict(int, {int(k): v for k, v in data.get('port_usage', {}).items()})

            stats = data.get('statistics', {})
            self.total_flows = stats.get('total_flows', 0)
            self.benign_flows = stats.get('benign_flows', 0)
            self.threat_flows = stats.get('threat_flows', 0)

            logger.info(f"Baseline loaded from {self.baseline_file}")
            logger.info(f"  Trusted IPs: {len(self.trusted_ips)}")
            logger.info(f"  Common flows: {len(self.common_flows)}")
            logger.info(f"  Ports learned: {len(self.port_usage)}")

        except Exception as e:
            logger.error(f"Failed to load baseline: {e}")

    def reset_baseline(self):
        """Reset baseline and start learning again."""
        self.trusted_ips = set()
        self.common_flows = defaultdict(int)
        self.port_usage = defaultdict(int)
        self.total_flows = 0
        self.benign_flows = 0
        self.threat_flows = 0
        self.start_time = time.time()

        if self.baseline_file.exists():
            self.baseline_file.unlink()

        logger.info("Baseline reset, starting fresh learning")


# Example usage
if __name__ == '__main__':
    # Create baseline
    baseline = AdaptiveBaseline(learning_period=3600)  # Learn for 1 hour

    # Simulate learning from normal traffic
    print("Simulating learning phase...")
    for i in range(100):
        baseline.learn_flow(
            src_ip='192.168.1.100',
            dst_ip='52.207.122.56',
            src_port=50000 + i,
            dst_port=443,
            is_benign=True
        )

    # Test evaluation
    result = baseline.evaluate_threat(
        src_ip='192.168.1.100',
        dst_ip='52.207.122.56',
        src_port=50001,
        dst_port=443,
        threat='DDoS-RSTFINFlood',
        confidence=0.96,
        packet_count=150
    )

    print("\nEvaluation result:")
    print(f"  Should alert: {result['should_alert']}")
    print(f"  Reason: {result['reason']}")
    print(f"  Original confidence: 0.96")
    print(f"  Adjusted confidence: {result['adjusted_confidence']:.2f}")
    print(f"  Adjustment: {result['confidence_adjustment']:.2f}")

    # Show statistics
    stats = baseline.get_statistics()
    print("\nBaseline statistics:")
    for key, value in stats.items():
        if key != 'top_ports':
            print(f"  {key}: {value}")
