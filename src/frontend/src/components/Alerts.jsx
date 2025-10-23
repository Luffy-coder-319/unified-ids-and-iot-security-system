import { useState, useEffect } from 'react';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  // Fetch existing alerts on component mount
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/alerts?limit=50');
        const data = await response.json();
        if (data.alerts && Array.isArray(data.alerts)) {
          setAlerts(data.alerts);
          setLoading(false);
        }
      } catch (err) {
        console.error('Error fetching alerts:', err);
        setLoading(false);
      }
    };

    fetchAlerts();
    // Poll for new alerts every 5 seconds
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  // WebSocket connection for real-time alerts
  useEffect(() => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/alerts');
      ws.onmessage = (event) => {
        const alert = JSON.parse(event.data);
        setAlerts(prev => [alert, ...prev].slice(0, 50)); // Keep last 50
      };
      return () => ws.close();
    } catch (err) {
      console.error('WebSocket error:', err);
    }
  }, []);

  // Filter alerts
  const filteredAlerts = filter === 'all'
    ? alerts
    : alerts.filter(alert => alert.severity === filter);

  // Get severity badge color
  const getSeverityColor = (severity) => {
    switch(severity) {
      case 'high': return 'bg-red-600 text-white';
      case 'medium': return 'bg-yellow-500 text-black';
      case 'low': return 'bg-green-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return <div className="text-center py-4 text-slate-400">Loading alerts...</div>;
  }

  return (
    <div>
      {/* Filter Buttons */}
      <div className="flex gap-2 mb-4 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          All ({alerts.length})
        </button>
        <button
          onClick={() => setFilter('high')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'high'
              ? 'bg-red-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          High ({alerts.filter(a => a.severity === 'high').length})
        </button>
        <button
          onClick={() => setFilter('medium')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'medium'
              ? 'bg-yellow-500 text-black'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Medium ({alerts.filter(a => a.severity === 'medium').length})
        </button>
        <button
          onClick={() => setFilter('low')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'low'
              ? 'bg-green-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Low ({alerts.filter(a => a.severity === 'low').length})
        </button>
      </div>

      {/* Alerts List */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-8 text-green-400 text-lg">
            No Threats Detected
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-slate-700 p-4 rounded-lg border-l-4 hover:bg-slate-600 transition-colors ${
                alert.severity === 'high' ? 'border-red-500' :
                alert.severity === 'medium' ? 'border-yellow-500' :
                'border-green-500'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg font-semibold text-white">
                       {alert.threat}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <div className="text-sm text-slate-300 space-y-1">
                    <div>
                      <span className="text-slate-400">From:</span> {alert.src}
                      <span className="text-slate-400 mx-2">→</span>
                      <span className="text-slate-400">To:</span> {alert.dst}
                    </div>
                    <div>
                      <span className="text-slate-400">Time:</span> {formatTime(alert.timestamp)}
                    </div>
                    <div>
                      <span className="text-slate-400">Status:</span>
                      <span className={`ml-2 ${alert.acknowledged ? 'text-green-400' : 'text-yellow-400'}`}>
                        {alert.acknowledged ? ' Acknowledged' : ' New'}
                      </span>
                    </div>
                    {alert.context && (
                      <div className="text-slate-400 text-xs mt-2">
                        {alert.context}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-slate-400 text-sm">
                  {alert.id}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Alerts;
