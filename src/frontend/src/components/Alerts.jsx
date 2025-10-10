import { useState, useEffect } from 'react';

function Alerts() {
  const [alerts, setAlerts] = useState([]);

  // Fetch existing alerts on component mount
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/alerts');
        const data = await response.json();
        if (data.alerts && Array.isArray(data.alerts)) {
          setAlerts(data.alerts);
        }
      } catch (err) {
        console.error('Error fetching alerts:', err);
      }
    };

    fetchAlerts();
    // Poll for new alerts every 5 seconds
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for real-time alerts
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/alerts');
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts(prev => [...prev, alert]);
    };
    return () => ws.close();
  }, []);

  return (
    <ul className="list-none p-0 space-y-2">
      {alerts.length === 0 ? <li className="text-green-400">No Threat Detected</li> : alerts.map((alert, index) => (
        <li key={index} className="text-red-400">
           {alert.threat} - {alert.severity} severity from {alert.src} to {alert.dst}: {alert.context}
        </li>
      ))}
    </ul>
  );
}

export default Alerts;
