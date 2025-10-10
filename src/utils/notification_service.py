import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Handles email and SMS notifications for critical security threats.
    """

    def __init__(self, config=None):
        """
        Initialize notification service with configuration.

        Args:
            config: Dictionary containing notification settings
        """
        self.config = config or {}
        self.email_enabled = self.config.get('email', {}).get('enabled', False)
        self.sms_enabled = self.config.get('sms', {}).get('enabled', False)

        # Email settings
        self.smtp_server = self.config.get('email', {}).get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('email', {}).get('smtp_port', 587)
        self.sender_email = self.config.get('email', {}).get('sender_email', '')
        self.sender_password = os.getenv('EMAIL_PASSWORD', self.config.get('email', {}).get('password', ''))
        self.recipient_emails = self.config.get('email', {}).get('recipients', [])

        # SMS settings (Twilio)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', self.config.get('sms', {}).get('account_sid', ''))
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', self.config.get('sms', {}).get('auth_token', ''))
        self.twilio_phone_number = self.config.get('sms', {}).get('from_number', '')
        self.recipient_phones = self.config.get('sms', {}).get('recipients', [])

        # Initialize Twilio client if SMS is enabled
        if self.sms_enabled and self.twilio_account_sid and self.twilio_auth_token:
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                self.sms_enabled = False

    def send_email_alert(self, alert):
        """
        Send email notification for a security alert.

        Args:
            alert: Dictionary containing alert details
        """
        if not self.email_enabled:
            return False

        try:
            subject = f"🚨 Security Alert: {alert.get('threat', 'Unknown')} - {alert.get('severity', 'unknown').upper()} Severity"

            body = f"""
            <html>
            <body>
                <h2>Security Threat Detected</h2>
                <p><strong>Threat Type:</strong> {alert.get('threat', 'Unknown')}</p>
                <p><strong>Severity:</strong> {alert.get('severity', 'unknown').upper()}</p>
                <p><strong>Source IP:</strong> {alert.get('src', 'Unknown')}</p>
                <p><strong>Destination IP:</strong> {alert.get('dst', 'Unknown')}</p>
                <p><strong>Context:</strong> {alert.get('context', 'No additional context')}</p>
                <p><strong>Timestamp:</strong> {alert.get('time', 'Unknown')}</p>

                {f"<p><strong>Anomaly Score:</strong> {alert.get('anomaly', {}).get('mse_normalized', 'N/A')}</p>" if 'anomaly' in alert else ''}

                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated alert from your IDS/IoT Security System.
                </p>
            </body>
            </html>
            """

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)

            html_part = MIMEText(body, 'html')
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info(f"Email alert sent for threat: {alert.get('threat')}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def send_sms_alert(self, alert):
        """
        Send SMS notification for a security alert.

        Args:
            alert: Dictionary containing alert details
        """
        if not self.sms_enabled:
            return False

        try:
            message_body = (
                f"🚨 IDS Alert: {alert.get('threat', 'Unknown')} "
                f"({alert.get('severity', 'unknown').upper()} severity) "
                f"from {alert.get('src', 'Unknown')}. "
                f"Check dashboard for details."
            )

            for phone in self.recipient_phones:
                self.twilio_client.messages.create(
                    body=message_body,
                    from_=self.twilio_phone_number,
                    to=phone
                )

            logger.info(f"SMS alert sent for threat: {alert.get('threat')}")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS alert: {e}")
            return False

    def send_alert(self, alert, severity_threshold='high'):
        """
        Send notification based on alert severity.

        Args:
            alert: Dictionary containing alert details
            severity_threshold: Minimum severity level to trigger notification
        """
        severity = alert.get('severity', 'low').lower()

        # Only send notifications for critical threats
        severity_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        threshold_level = severity_levels.get(severity_threshold.lower(), 2)
        alert_level = severity_levels.get(severity, 0)

        if alert_level >= threshold_level:
            email_sent = self.send_email_alert(alert)
            sms_sent = self.send_sms_alert(alert)

            return email_sent or sms_sent

        return False

    def send_summary_report(self, stats):
        """
        Send periodic summary report via email.

        Args:
            stats: Dictionary containing threat statistics
        """
        if not self.email_enabled:
            return False

        try:
            subject = f"📊 IDS Security Report - {stats.get('period', 'Daily')}"

            body = f"""
            <html>
            <body>
                <h2>Security Summary Report</h2>
                <p><strong>Report Period:</strong> {stats.get('period', 'N/A')}</p>
                <p><strong>Total Alerts:</strong> {stats.get('total_alerts', 0)}</p>

                <h3>Alerts by Severity</h3>
                <ul>
                    <li>High: {stats.get('high_severity', 0)}</li>
                    <li>Medium: {stats.get('medium_severity', 0)}</li>
                    <li>Low: {stats.get('low_severity', 0)}</li>
                </ul>

                <h3>Top Threats</h3>
                <ul>
                    {"".join([f"<li>{threat}: {count} occurrences</li>" for threat, count in stats.get('top_threats', {}).items()])}
                </ul>

                <h3>Top Source IPs</h3>
                <ul>
                    {"".join([f"<li>{ip}: {count} threats</li>" for ip, count in stats.get('top_sources', {}).items()])}
                </ul>

                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated report from your IDS/IoT Security System.
                </p>
            </body>
            </html>
            """

            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)

            html_part = MIMEText(body, 'html')
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            logger.info("Summary report sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send summary report: {e}")
            return False
