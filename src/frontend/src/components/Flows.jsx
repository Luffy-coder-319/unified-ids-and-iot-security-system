import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Flows() {
  const [flows, setFlows] = useState([]);

  // WebSocket connection for real-time flows
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/flows');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setFlows(data);
    };
    return () => ws.close();
  }, []);

  // Prepare data for chart
  const chartData = flows.map((flow, index) => ({
    name: `Flow ${index + 1}`,
    packets: flow.pkt_count,
    key: flow.key
  }));

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-green-400">Network Flows</h2>
      {flows.length === 0 ? (
        <p className="text-gray-400">No flows yet</p>
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
