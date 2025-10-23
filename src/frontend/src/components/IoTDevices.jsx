import { useState, useEffect } from 'react';

function IoTDevices() {
  const [devices, setDevices] = useState([]);
  const [summary, setSummary] = useState({ total_devices: 0, iot_devices: 0, non_iot_devices: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'iot', 'non-iot'

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch devices
        const devicesRes = await fetch('http://localhost:8000/api/iot/devices');
        if (!devicesRes.ok) throw new Error('Failed to fetch IoT devices');
        const devicesData = await devicesRes.json();

        // Fetch summary
        const summaryRes = await fetch('http://localhost:8000/api/iot/summary');
        if (!summaryRes.ok) throw new Error('Failed to fetch summary');
        const summaryData = await summaryRes.json();

        setDevices(devicesData.devices || []);
        setSummary(summaryData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching IoT devices:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchDevices();
    const interval = setInterval(fetchDevices, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // Filter devices
  const filteredDevices = devices.filter(device => {
    if (filter === 'iot') return device.is_iot === true;
    if (filter === 'non-iot') return device.is_iot === false;
    return true; // 'all'
  });

  // Get confidence badge color
  const getConfidenceBadge = (confidence) => {
    if (confidence === 'high') return 'bg-green-500 text-white';
    if (confidence === 'medium') return 'bg-yellow-500 text-slate-900';
    return 'bg-slate-600 text-slate-300';
  };

  // Get device type icon
  const getDeviceIcon = (deviceType) => {
    if (!deviceType) return '🖥️';
    const type = deviceType.toLowerCase();
    if (type.includes('raspberry')) return '🍓';
    if (type.includes('echo') || type.includes('alexa')) return '🔊';
    if (type.includes('google') || type.includes('nest')) return '🏠';
    if (type.includes('camera') || type.includes('cam')) return '📹';
    if (type.includes('hue') || type.includes('light')) return '💡';
    if (type.includes('thermostat')) return '🌡️';
    if (type.includes('plug')) return '🔌';
    if (type.includes('esp') || type.includes('arduino')) return '🔧';
    return '📱';
  };

  // Format time
  const formatTime = (isoString) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
  };

  if (loading && devices.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        <p className="mt-4 text-slate-400">Loading IoT devices...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
        <p className="text-red-400 mb-2">⚠️ Error loading IoT devices</p>
        <p className="text-sm text-slate-400">{error}</p>
        <p className="text-xs text-slate-500 mt-2">Make sure the server is running with IoT detection enabled.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-700 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-blue-400">{summary.total_devices || 0}</div>
          <div className="text-sm text-slate-400 mt-1">Total Devices</div>
        </div>
        <div className="bg-slate-700 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-green-400">{summary.iot_devices || 0}</div>
          <div className="text-sm text-slate-400 mt-1">IoT Devices</div>
        </div>
        <div className="bg-slate-700 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-emerald-400">{summary.high_confidence || 0}</div>
          <div className="text-sm text-slate-400 mt-1">High Confidence</div>
        </div>
        <div className="bg-slate-700 p-4 rounded-lg text-center">
          <div className="text-3xl font-bold text-yellow-400">{summary.medium_confidence || 0}</div>
          <div className="text-sm text-slate-400 mt-1">Medium Confidence</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'all' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          All Devices ({devices.length})
        </button>
        <button
          onClick={() => setFilter('iot')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'iot' ? 'bg-green-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          IoT Only ({summary.iot_devices || 0})
        </button>
        <button
          onClick={() => setFilter('non-iot')}
          className={`px-4 py-2 rounded-lg transition-colors ${
            filter === 'non-iot' ? 'bg-slate-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          }`}
        >
          Non-IoT ({summary.non_iot_devices || 0})
        </button>
      </div>

      {/* Devices List */}
      {filteredDevices.length === 0 ? (
        <div className="text-center py-12 bg-slate-700/50 rounded-lg">
          <p className="text-slate-400 text-lg mb-2">No devices detected yet</p>
          <p className="text-sm text-slate-500">Devices will appear as they communicate on the network.</p>
          <p className="text-xs text-slate-600 mt-2">Try pinging your IoT devices to generate traffic.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDevices.map((device, index) => (
            <div
              key={device.mac_address || index}
              className={`bg-slate-700 rounded-lg p-4 border-l-4 ${
                device.is_iot ? 'border-green-500' : 'border-slate-500'
              } hover:bg-slate-600 transition-colors`}
            >
              {/* Device Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-3xl">{getDeviceIcon(device.device_type)}</span>
                  <div>
                    {/* Primary name - use friendly_name if available, otherwise hostname, then device_type */}
                    <h3 className="font-semibold text-slate-100 text-lg">
                      {device.friendly_name || device.hostname || device.device_type || 'Unknown Device'}
                    </h3>
                    {/* Secondary info - show device type if different from friendly name */}
                    {device.friendly_name && device.device_type && device.friendly_name !== device.device_type && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        {device.device_type}
                      </p>
                    )}
                    <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${getConfidenceBadge(device.confidence)}`}>
                      {device.confidence?.toUpperCase() || 'UNKNOWN'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Device Details */}
              <div className="space-y-2 text-sm">
                {/* Show hostname if available and different from friendly name */}
                {device.hostname && device.hostname !== device.friendly_name && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Hostname:</span>
                    <span className="text-slate-200 font-mono">{device.hostname}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-400">IP Address:</span>
                  <span className="text-slate-200 font-mono">{device.ip_address}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">MAC Address:</span>
                  <span className="text-slate-300 font-mono text-xs">{device.mac_address || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Packets:</span>
                  <span className="text-slate-200">{device.packet_count || 0}</span>
                </div>
                {device.last_seen && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Last Seen:</span>
                    <span className="text-slate-200">{formatTime(device.last_seen)}</span>
                  </div>
                )}
              </div>

              {/* Ports & Protocols */}
              {device.ports_used && device.ports_used.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-600">
                  <div className="text-xs text-slate-400 mb-1">Ports:</div>
                  <div className="flex flex-wrap gap-1">
                    {device.ports_used.slice(0, 6).map(port => (
                      <span key={port} className="bg-slate-800 px-2 py-1 rounded text-xs text-slate-300">
                        {port}
                      </span>
                    ))}
                    {device.ports_used.length > 6 && (
                      <span className="text-xs text-slate-500">+{device.ports_used.length - 6} more</span>
                    )}
                  </div>
                </div>
              )}

              {device.protocols_seen && device.protocols_seen.length > 0 && (
                <div className="mt-2">
                  <div className="text-xs text-slate-400 mb-1">Protocols:</div>
                  <div className="flex flex-wrap gap-1">
                    {device.protocols_seen.map(proto => (
                      <span key={proto} className="bg-blue-900/30 text-blue-300 px-2 py-1 rounded text-xs">
                        {proto}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Detection Method */}
              {device.detection_method && (
                <div className="mt-3 text-xs text-slate-500">
                  Detected via: {device.detection_method.replace('_', ' ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default IoTDevices;
