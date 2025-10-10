import paho.mqtt.client as mqtt
import logging

logger = logging.getLogger(__name__)

class MQTTSecurity:
    def __init__(self, broker='localhost', port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")
        client.subscribe("iot/#")  # Subscribe to all IoT topics

    def on_message(self, client, userdata, msg):
        # Analyze MQTT message for security
        self.analyze_message(msg.topic, msg.payload)

    def analyze_message(self, topic, payload):
        # Basic security checks
        if len(payload) > 1024:  # Large payload
            logger.warning(f"Large payload on topic {topic}")
        if b'password' in payload.lower() or b'key' in payload.lower():
            logger.warning(f"Sensitive data detected on topic {topic}")
        # Add more checks as needed

    def start_monitoring(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def stop_monitoring(self):
        self.client.loop_stop()
        self.client.disconnect()
