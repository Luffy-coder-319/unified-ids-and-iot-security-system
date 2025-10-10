import time
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
import threading

class StatisticsTracker:
    """
    Tracks and aggregates security threat statistics for reporting.
    """

    def __init__(self, storage_path='logs/statistics.json'):
        """
        Initialize the statistics tracker.

        Args:
            storage_path: Path to store statistics data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory statistics
        self.alerts_by_severity = defaultdict(int)
        self.alerts_by_type = defaultdict(int)
        self.alerts_by_source = defaultdict(int)
        self.alerts_by_destination = defaultdict(int)
        self.hourly_alerts = defaultdict(int)
        self.total_alerts = 0
        self.start_time = time.time()

        # Thread lock for concurrent access
        self.lock = threading.Lock()

        # Load existing statistics
        self._load_statistics()

    def _load_statistics(self):
        """Load statistics from storage file."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.alerts_by_severity = defaultdict(int, data.get('alerts_by_severity', {}))
                    self.alerts_by_type = defaultdict(int, data.get('alerts_by_type', {}))
                    self.alerts_by_source = defaultdict(int, data.get('alerts_by_source', {}))
                    self.alerts_by_destination = defaultdict(int, data.get('alerts_by_destination', {}))
                    self.hourly_alerts = defaultdict(int, data.get('hourly_alerts', {}))
                    self.total_alerts = data.get('total_alerts', 0)
                    self.start_time = data.get('start_time', time.time())
        except Exception as e:
            print(f"[StatisticsTracker] Failed to load statistics: {e}")

    def _save_statistics(self):
        """Save statistics to storage file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump({
                    'alerts_by_severity': dict(self.alerts_by_severity),
                    'alerts_by_type': dict(self.alerts_by_type),
                    'alerts_by_source': dict(self.alerts_by_source),
                    'alerts_by_destination': dict(self.alerts_by_destination),
                    'hourly_alerts': dict(self.hourly_alerts),
                    'total_alerts': self.total_alerts,
                    'start_time': self.start_time,
                    'last_updated': time.time()
                }, f, indent=2)
        except Exception as e:
            print(f"[StatisticsTracker] Failed to save statistics: {e}")

    def record_alert(self, alert):
        """
        Record an alert in the statistics.

        Args:
            alert: Dictionary containing alert details
        """
        with self.lock:
            self.total_alerts += 1

            # Track by severity
            severity = alert.get('severity', 'unknown').lower()
            self.alerts_by_severity[severity] += 1

            # Track by threat type
            threat = alert.get('threat', 'unknown')
            self.alerts_by_type[threat] += 1

            # Track by source IP
            source = alert.get('src', 'unknown')
            self.alerts_by_source[source] += 1

            # Track by destination IP
            destination = alert.get('dst', 'unknown')
            self.alerts_by_destination[destination] += 1

            # Track by hour
            current_hour = datetime.now().strftime('%Y-%m-%d %H:00')
            self.hourly_alerts[current_hour] += 1

            # Save to disk
            self._save_statistics()

    def get_summary(self, period='all'):
        """
        Get summary statistics for a given period.

        Args:
            period: 'hourly', 'daily', 'weekly', or 'all'

        Returns:
            Dictionary containing summary statistics
        """
        with self.lock:
            if period == 'all':
                return self._get_all_time_summary()
            elif period == 'hourly':
                return self._get_hourly_summary()
            elif period == 'daily':
                return self._get_daily_summary()
            elif period == 'weekly':
                return self._get_weekly_summary()
            else:
                return self._get_all_time_summary()

    def _get_all_time_summary(self):
        """Get all-time statistics summary."""
        return {
            'period': 'All Time',
            'total_alerts': self.total_alerts,
            'high_severity': self.alerts_by_severity.get('high', 0),
            'medium_severity': self.alerts_by_severity.get('medium', 0),
            'low_severity': self.alerts_by_severity.get('low', 0),
            'top_threats': dict(Counter(self.alerts_by_type).most_common(5)),
            'top_sources': dict(Counter(self.alerts_by_source).most_common(5)),
            'top_destinations': dict(Counter(self.alerts_by_destination).most_common(5)),
            'alerts_by_type': dict(self.alerts_by_type),
            'alerts_by_severity': dict(self.alerts_by_severity),
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'uptime_hours': (time.time() - self.start_time) / 3600
        }

    def _get_hourly_summary(self):
        """Get last hour statistics."""
        current_hour = datetime.now().strftime('%Y-%m-%d %H:00')
        alerts_this_hour = self.hourly_alerts.get(current_hour, 0)

        return {
            'period': 'Last Hour',
            'total_alerts': alerts_this_hour,
            'hour': current_hour
        }

    def _get_daily_summary(self):
        """Get last 24 hours statistics."""
        now = datetime.now()
        last_24_hours = []
        total_alerts_24h = 0

        for i in range(24):
            hour = (now - timedelta(hours=i)).strftime('%Y-%m-%d %H:00')
            alerts = self.hourly_alerts.get(hour, 0)
            total_alerts_24h += alerts
            last_24_hours.append({'hour': hour, 'alerts': alerts})

        return {
            'period': 'Last 24 Hours',
            'total_alerts': total_alerts_24h,
            'hourly_breakdown': list(reversed(last_24_hours))
        }

    def _get_weekly_summary(self):
        """Get last 7 days statistics."""
        now = datetime.now()
        last_7_days = defaultdict(int)

        for i in range(7 * 24):  # 7 days * 24 hours
            hour = (now - timedelta(hours=i)).strftime('%Y-%m-%d %H:00')
            day = hour[:10]  # Extract date (YYYY-MM-DD)
            last_7_days[day] += self.hourly_alerts.get(hour, 0)

        total_alerts_7d = sum(last_7_days.values())

        return {
            'period': 'Last 7 Days',
            'total_alerts': total_alerts_7d,
            'daily_breakdown': [{'date': date, 'alerts': count} for date, count in sorted(last_7_days.items())]
        }

    def get_real_time_stats(self):
        """
        Get real-time statistics for dashboard display.

        Returns:
            Dictionary with current statistics
        """
        with self.lock:
            return {
                'total_alerts': self.total_alerts,
                'alerts_by_severity': dict(self.alerts_by_severity),
                'alerts_by_type': dict(self.alerts_by_type),
                'top_sources': dict(Counter(self.alerts_by_source).most_common(10)),
                'recent_hourly': dict(sorted(self.hourly_alerts.items())[-24:])
            }

    def reset_statistics(self):
        """Reset all statistics (useful for testing or periodic resets)."""
        with self.lock:
            self.alerts_by_severity.clear()
            self.alerts_by_type.clear()
            self.alerts_by_source.clear()
            self.alerts_by_destination.clear()
            self.hourly_alerts.clear()
            self.total_alerts = 0
            self.start_time = time.time()
            self._save_statistics()
