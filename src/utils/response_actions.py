import subprocess
import logging
import time
from collections import defaultdict
from threading import Lock

logger = logging.getLogger(__name__)

class ResponseActionManager:
    """
    Manages automated defensive responses to detected threats.
    """

    def __init__(self, config=None):
        """
        Initialize the response action manager.

        Args:
            config: Dictionary containing response configuration
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.auto_block_high = self.config.get('auto_block_high_severity', True)
        self.auto_block_medium = self.config.get('auto_block_medium_severity', False)
        self.rate_limit_threshold = self.config.get('rate_limit_threshold', 100)  # packets/sec
        self.temp_block_duration = self.config.get('temp_block_duration', 3600)  # seconds

        # Track blocked IPs
        self.blocked_ips = {}  # {ip: {'timestamp': time, 'reason': str, 'permanent': bool}}
        self.rate_limited_ips = defaultdict(list)  # {ip: [timestamps]}
        self.lock = Lock()

        # Action history
        self.action_history = []

    def _log_action(self, action_type, target, reason, success):
        """
        Log a defensive action.

        Args:
            action_type: Type of action taken
            target: Target of the action (e.g., IP address)
            reason: Reason for the action
            success: Whether the action was successful
        """
        action = {
            'timestamp': time.time(),
            'action_type': action_type,
            'target': target,
            'reason': reason,
            'success': success
        }
        self.action_history.append(action)
        logger.info(f"Action logged: {action}")

    def block_ip(self, ip_address, reason='threat_detected', permanent=False):
        """
        Block an IP address using iptables.

        Args:
            ip_address: IP address to block
            reason: Reason for blocking
            permanent: Whether block is permanent or temporary

        Returns:
            Boolean indicating success
        """
        if not self.enabled:
            logger.info(f"Response actions disabled. Would have blocked {ip_address}")
            return False

        with self.lock:
            # Check if already blocked
            if ip_address in self.blocked_ips:
                logger.info(f"IP {ip_address} already blocked")
                return True

            try:
                # Add iptables rule to block IP
                result = subprocess.run(
                    ['sudo', 'iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    self.blocked_ips[ip_address] = {
                        'timestamp': time.time(),
                        'reason': reason,
                        'permanent': permanent
                    }
                    self._log_action('block_ip', ip_address, reason, True)
                    logger.info(f"Successfully blocked IP: {ip_address} (Reason: {reason})")
                    return True
                else:
                    logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
                    self._log_action('block_ip', ip_address, reason, False)
                    return False

            except subprocess.TimeoutExpired:
                logger.error(f"Timeout while blocking IP {ip_address}")
                self._log_action('block_ip', ip_address, reason, False)
                return False
            except Exception as e:
                logger.error(f"Error blocking IP {ip_address}: {e}")
                self._log_action('block_ip', ip_address, reason, False)
                return False

    def unblock_ip(self, ip_address):
        """
        Unblock an IP address.

        Args:
            ip_address: IP address to unblock

        Returns:
            Boolean indicating success
        """
        if not self.enabled:
            logger.info(f"Response actions disabled. Would have unblocked {ip_address}")
            return False

        with self.lock:
            if ip_address not in self.blocked_ips:
                logger.info(f"IP {ip_address} is not currently blocked")
                return False

            try:
                # Remove iptables rule
                result = subprocess.run(
                    ['sudo', 'iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    del self.blocked_ips[ip_address]
                    self._log_action('unblock_ip', ip_address, 'manual_unblock', True)
                    logger.info(f"Successfully unblocked IP: {ip_address}")
                    return True
                else:
                    logger.error(f"Failed to unblock IP {ip_address}: {result.stderr}")
                    self._log_action('unblock_ip', ip_address, 'manual_unblock', False)
                    return False

            except Exception as e:
                logger.error(f"Error unblocking IP {ip_address}: {e}")
                self._log_action('unblock_ip', ip_address, 'manual_unblock', False)
                return False

    def rate_limit_ip(self, ip_address, rate):
        """
        Apply rate limiting to an IP address using iptables.

        Args:
            ip_address: IP address to rate limit
            rate: Rate limit (e.g., '10/second', '100/minute')

        Returns:
            Boolean indicating success
        """
        if not self.enabled:
            logger.info(f"Response actions disabled. Would have rate-limited {ip_address}")
            return False

        try:
            # Add rate limiting rule
            result = subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', ip_address,
                '-m', 'limit', '--limit', rate,
                '-j', 'ACCEPT'
            ], capture_output=True, text=True, timeout=10)

            # Drop packets exceeding rate
            subprocess.run([
                'sudo', 'iptables', '-A', 'INPUT',
                '-s', ip_address,
                '-j', 'DROP'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self._log_action('rate_limit', ip_address, f'rate={rate}', True)
                logger.info(f"Applied rate limit to IP: {ip_address} ({rate})")
                return True
            else:
                logger.error(f"Failed to rate-limit IP {ip_address}: {result.stderr}")
                self._log_action('rate_limit', ip_address, f'rate={rate}', False)
                return False

        except Exception as e:
            logger.error(f"Error rate-limiting IP {ip_address}: {e}")
            self._log_action('rate_limit', ip_address, f'rate={rate}', False)
            return False

    def handle_threat(self, alert):
        """
        Automatically handle a detected threat based on severity.

        Args:
            alert: Dictionary containing alert details

        Returns:
            Dictionary with actions taken
        """
        severity = alert.get('severity', 'low').lower()
        source_ip = alert.get('src')
        threat_type = alert.get('threat', 'unknown')

        actions_taken = []

        if not source_ip or source_ip == 'unknown':
            logger.warning("Cannot take action: no source IP in alert")
            return {'actions_taken': [], 'success': False}

        # High severity: immediate block
        if severity == 'high' and self.auto_block_high:
            success = self.block_ip(source_ip, f'{threat_type}_high_severity', permanent=False)
            actions_taken.append({
                'action': 'block_ip',
                'target': source_ip,
                'success': success
            })

        # Medium severity: rate limit or temporary block
        elif severity == 'medium' and self.auto_block_medium:
            success = self.rate_limit_ip(source_ip, '10/second')
            actions_taken.append({
                'action': 'rate_limit',
                'target': source_ip,
                'success': success
            })

        # Low severity: log only (no automated action)
        elif severity == 'low':
            logger.info(f"Low severity threat from {source_ip}: monitoring only")
            actions_taken.append({
                'action': 'monitor',
                'target': source_ip,
                'success': True
            })

        return {
            'actions_taken': actions_taken,
            'success': any(action['success'] for action in actions_taken)
        }

    def check_and_unblock_expired(self):
        """
        Check for and unblock temporarily blocked IPs that have expired.

        Returns:
            List of unblocked IPs
        """
        current_time = time.time()
        unblocked = []

        with self.lock:
            expired_ips = []

            for ip, block_info in self.blocked_ips.items():
                if not block_info['permanent']:
                    if current_time - block_info['timestamp'] >= self.temp_block_duration:
                        expired_ips.append(ip)

            for ip in expired_ips:
                if self.unblock_ip(ip):
                    unblocked.append(ip)
                    logger.info(f"Automatically unblocked expired IP: {ip}")

        return unblocked

    def get_blocked_ips(self):
        """
        Get list of currently blocked IPs.

        Returns:
            Dictionary of blocked IPs with their details
        """
        with self.lock:
            return self.blocked_ips.copy()

    def get_action_history(self, limit=100):
        """
        Get history of actions taken.

        Args:
            limit: Maximum number of actions to return

        Returns:
            List of recent actions
        """
        return self.action_history[-limit:]

    def whitelist_ip(self, ip_address):
        """
        Add an IP to whitelist (prevent future blocking).

        Args:
            ip_address: IP to whitelist

        Returns:
            Boolean indicating success
        """
        try:
            # Add iptables rule to accept from this IP (high priority)
            result = subprocess.run([
                'sudo', 'iptables', '-I', 'INPUT', '1',
                '-s', ip_address,
                '-j', 'ACCEPT'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self._log_action('whitelist', ip_address, 'manual_whitelist', True)
                logger.info(f"Successfully whitelisted IP: {ip_address}")
                return True
            else:
                logger.error(f"Failed to whitelist IP {ip_address}: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error whitelisting IP {ip_address}: {e}")
            return False
