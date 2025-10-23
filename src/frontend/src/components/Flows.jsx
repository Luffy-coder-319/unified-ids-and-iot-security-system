import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Flows() {
  const [flows, setFlows] = useState([]);
  const [useWebSocket, setUseWebSocket] = useState(true);
  const [error, setError] = useState(null);

  // Try WebSocket connection first, fallback to REST API
  useEffect(() => {
    if (useWebSocket) {
      try {
        const ws = new WebSocket('ws://localhost:8000/ws/flows');

        ws.onopen = () => {
          console.log('WebSocket connected for flows');
          setError(null);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          setFlows(data);
        };

        ws.onerror = (err) => {
          console.error('WebSocket error, falling back to REST API:', err);
          setUseWebSocket(false);
          setError('WebSocket failed, using REST API');
        };

        ws.onclose = () => {
          console.log('WebSocket closed, falling back to REST API');
          setUseWebSocket(false);
        };

        return () => ws.close();
      } catch (err) {
        console.error('WebSocket initialization failed:', err);
        setUseWebSocket(false);
      }
    } else {
      // Fallback to REST API polling
      const fetchFlows = async () => {
        try {
          const response = await fetch('http://localhost:8000/api/flows');
          if (response.ok) {
            const data = await response.json();
            setFlows(data);
            setError(null);
          } else {
            setError('Failed to fetch flows');
          }
        } catch (err) {
          console.error('Error fetching flows:', err);
          setError('Cannot connect to API');
        }
      };

      fetchFlows();
      const interval = setInterval(fetchFlows, 2000); // Poll every 2 seconds
      return () => clearInterval(interval);
    }
  }, [useWebSocket]);

  // Prepare data for chart
  const chartData = flows.map((flow, index) => ({
    name: `Flow ${index + 1}`,
    packets: flow.pkt_count,
    key: flow.key
  }));

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-green-400">Network Flows</h2>
        <div className="text-sm text-gray-400">
          {useWebSocket ? '🟢 Live' : '🔄 Polling'}
          {error && <span className="ml-2 text-yellow-400">({error})</span>}
        </div>
      </div>
      {flows.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400 mb-2">No network flows detected yet</p>
          <p className="text-gray-500 text-sm">Start browsing or generate network activity to see flows</p>
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#f3f4f6' }}
                formatter={(value, name) => [value, 'Packets']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="packets"
                stroke="#10b981"
                strokeWidth={3}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2, fill: '#065f46' }}
              />
            </LineChart>
          </ResponsiveContainer>
         {/*<div className="space-y-2">
            {flows.map((flow, index) => (
              <div key={index} className="p-2 bg-green-100 rounded">
                <strong>Flow {index + 1}:</strong> {flow.key} - {flow.pkt_count} packets
              </div>
            ))}
          </div> */}
        </>
      )}
    </div>
  );
}

export default Flows;
