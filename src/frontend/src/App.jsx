import { useState, useEffect } from 'react';
import Alerts from './components/Alerts';
import Flows from './components/Flows';

function App() {
  const [stats, setStats] = useState({ packets: 0, threats: 0, devices: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const flowsRes = await fetch('http://localhost:8000/flows');
        const flows = await flowsRes.json();
        const totalPackets = flows.reduce((sum, flow) => sum + flow.pkt_count, 0);
        const uniqueDevices = new Set(flows.map(flow => flow.key.split('->')[0])).size; // rough estimate

        const alertsRes = await fetch('http://localhost:8000/alerts');
        const alerts = await alertsRes.json();

        setStats({
          packets: totalPackets,
          threats: alerts.length,
          devices: uniqueDevices
        });
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 text-slate-100 font-sans flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-56 bg-slate-800 p-4 h-screen fixed">
        <h2 className="text-green-500 text-center text-xl font-bold">UCS</h2>
        <ul className="list-none p-0 mt-4">
          <li className="p-2.5 m-2 bg-slate-700 rounded-md cursor-pointer transition-colors hover:bg-blue-600">📊 Dashboard</li>
          <li className="p-2.5 m-2 bg-slate-700 rounded-md cursor-pointer transition-colors hover:bg-blue-600">🖥 Devices</li>
          <li className="p-2.5 m-2 bg-slate-700 rounded-md cursor-pointer transition-colors hover:bg-blue-600">⚠️ Threat Logs</li>
          <li className="p-2.5 m-2 bg-slate-700 rounded-md cursor-pointer transition-colors hover:bg-blue-600">📑 Reports</li>

        </ul>
      </aside>

      {/* Main content */}
      <div className="ml-60 flex-1 p-8">
        <header className="text-center mb-8">
          <h1 className="text-green-500 text-3xl font-bold">Unified Cybersecurity System</h1>
          <p className="text-lg">Threat Detection & IoT Security</p>
        </header>

        <section className="flex gap-6 mb-8">
          <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40">
            <h3 className="mb-4 text-xl font-semibold">Total Packets</h3>
            <p className="text-2xl font-bold" id="packets-count">{stats.packets}</p>
          </div>
          <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40 border-l-4 border-red-500">
            <h3 className="mb-4 text-xl font-semibold">Detected Threats</h3>
            <p className="text-2xl font-bold" id="threats-count">{stats.threats}</p>
          </div>
          <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40 border-l-4 border-green-500">
            <h3 className="mb-4 text-xl font-semibold">Active Devices</h3>
            <p className="text-2xl font-bold" id="devices-count">{stats.devices}</p>
          </div>
        </section>

        <section className="bg-slate-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-semibold mb-4">Traffic Overview</h2>
          <Flows />
        </section>

        <section className="bg-slate-800 p-6 rounded-xl mb-8">
          <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
          <Alerts />
        </section>

        <footer className="text-center mt-4 p-4 bg-slate-800 rounded-lg">
          <p>© 2025 Unified Cybersecurity System | Project by Natasha and Tanyaradzwa</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
