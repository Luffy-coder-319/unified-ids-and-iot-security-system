import time
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from threading import Lock

class AlertManager:
    """
    Manages alert acknowledgments and tracking of reviewed threats.
    """

    @staticmethod
    def _sanitize_for_json(obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(obj, dict):
            return {k: AlertManager._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [AlertManager._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist() if obj.size > 1 else float(obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        else:
            return obj

    def __init__(self, storage_path='logs/alert_tracking.json'):
        """
        Initialize the alert manager.

        Args:
            storage_path: Path to store alert tracking data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Alert tracking
        self.alerts = []  # List of all alerts
        self.acknowledged_alerts = set()  # IDs of acknowledged alerts
        self.alert_counter = 0
        self.lock = Lock()

        # Load existing data
        self._load_data()

    def _load_data(self):
        """Load alert tracking data from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.alerts = data.get('alerts', [])
                    self.acknowledged_alerts = set(data.get('acknowledged_alerts', []))
                    self.alert_counter = data.get('alert_counter', 0)
        except Exception as e:
            print(f"[AlertManager] Failed to load data: {e}")

    def _save_data(self):
        """Save alert tracking data to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({
                    'alerts': self.alerts,
                    'acknowledged_alerts': list(self.acknowledged_alerts),
                    'alert_counter': self.alert_counter,
                    'last_updated': time.time()
                }, f, indent=2)
        except Exception as e:
            print(f"[AlertManager] Failed to save data: {e}")

    def add_alert(self, alert):
        """
        Add a new alert to the tracking system.

        Args:
            alert: Dictionary containing alert details

        Returns:
            Alert ID
        """
        with self.lock:
            self.alert_counter += 1
            alert_id = self.alert_counter

            # Enhance alert with metadata
            tracked_alert = {
                'id': alert_id,
                'timestamp': alert.get('time', time.time()),
                'threat': alert.get('threat', 'unknown'),
                'severity': alert.get('severity', 'unknown'),
                'src': alert.get('src', 'unknown'),
                'dst': alert.get('dst', 'unknown'),
                'context': alert.get('context', ''),
                'anomaly': self._sanitize_for_json(alert.get('anomaly', {})),
                'acknowledged': False,
                'acknowledged_by': None,
                'acknowledged_at': None,
                'notes': '',
                'status': 'new'  # new, investigating, resolved, false_positive
            }

            self.alerts.append(tracked_alert)
            self._save_data()

            return alert_id

    def acknowledge_alert(self, alert_id, user='system', notes=''):
        """
        Mark an alert as acknowledged.

        Args:
            alert_id: ID of the alert to acknowledge
            user: User who acknowledged the alert
            notes: Optional notes about the acknowledgment

        Returns:
            Boolean indicating success
        """
        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['acknowledged'] = True
                    alert['acknowledged_by'] = user
                    alert['acknowledged_at'] = time.time()
                    alert['notes'] = notes
                    self.acknowledged_alerts.add(alert_id)
                    self._save_data()
                    return True

            return False

    def update_alert_status(self, alert_id, status, notes=''):
        """
        Update the status of an alert.

        Args:
            alert_id: ID of the alert
            status: New status ('new', 'investigating', 'resolved', 'false_positive')
            notes: Optional notes about the status change

        Returns:
            Boolean indicating success
        """
        valid_statuses = ['new', 'investigating', 'resolved', 'false_positive']
        if status not in valid_statuses:
            return False

        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['status'] = status
                    if notes:
                        alert['notes'] = notes
                    self._save_data()
                    return True

            return False

    def get_alert(self, alert_id):
        """
        Get details of a specific alert.

        Args:
            alert_id: ID of the alert

        Returns:
            Alert dictionary or None if not found
        """
        with self.lock:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    return alert.copy()

            return None

    def get_alerts(self, filters=None, limit=None):
        """
        Get list of alerts with optional filtering.

        Args:
            filters: Dictionary with filter criteria
                - severity: Filter by severity level
                - threat: Filter by threat type
                - acknowledged: Filter by acknowledgment status
                - status: Filter by status
                - src: Filter by source IP
            limit: Maximum number of alerts to return

        Returns:
            List of alerts matching the filters
        """
        with self.lock:
            filtered_alerts = self.alerts.copy()

            if filters:
                if 'severity' in filters:
                    filtered_alerts = [a for a in filtered_alerts if a['severity'] == filters['severity']]

                if 'threat' in filters:
                    filtered_alerts = [a for a in filtered_alerts if a['threat'] == filters['threat']]

                if 'acknowledged' in filters:
                    ack_filter = filters['acknowledged']
                    filtered_alerts = [a for a in filtered_alerts if a['acknowledged'] == ack_filter]

                if 'status' in filters:
                    filtered_alerts = [a for a in filtered_alerts if a['status'] == filters['status']]

                if 'src' in filters:
                    filtered_alerts = [a for a in filtered_alerts if a['src'] == filters['src']]

            # Sort by timestamp (most recent first)
            filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)

            if limit:
                filtered_alerts = filtered_alerts[:limit]

            return filtered_alerts

    def get_unacknowledged_count(self):
        """
        Get count of unacknowledged alerts.

        Returns:
            Number of unacknowledged alerts
        """
        with self.lock:
            return sum(1 for alert in self.alerts if not alert['acknowledged'])

    def get_alerts_by_severity(self):
        """
        Get count of alerts grouped by severity.

        Returns:
            Dictionary with severity counts
        """
        with self.lock:
            severity_counts = defaultdict(int)
            for alert in self.alerts:
                severity_counts[alert['severity']] += 1

            return dict(severity_counts)

    def get_alerts_by_status(self):
        """
        Get count of alerts grouped by status.

        Returns:
            Dictionary with status counts
        """
        with self.lock:
            status_counts = defaultdict(int)
            for alert in self.alerts:
                status_counts[alert['status']] += 1

            return dict(status_counts)

    def get_recent_alerts(self, count=10):
        """
        Get most recent alerts.

        Args:
            count: Number of recent alerts to return

        Returns:
            List of recent alerts
        """
        return self.get_alerts(limit=count)

    def clear_old_alerts(self, days=30):
        """
        Remove alerts older than specified days.

        Args:
            days: Number of days to keep alerts

        Returns:
            Number of alerts removed
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        with self.lock:
            initial_count = len(self.alerts)
            self.alerts = [a for a in self.alerts if a['timestamp'] >= cutoff_time]
            removed_count = initial_count - len(self.alerts)

            # Clean up acknowledged set
            valid_ids = {a['id'] for a in self.alerts}
            self.acknowledged_alerts = self.acknowledged_alerts.intersection(valid_ids)

            self._save_data()

            return removed_count
