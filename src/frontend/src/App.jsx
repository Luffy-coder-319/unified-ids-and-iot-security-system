import { useState, useEffect } from 'react';
import Alerts from './components/Alerts';
import Flows from './components/Flows';
import IoTDevices from './components/IoTDevices';
import { LuRadioTower } from 'react-icons/lu';
import { MdOutlineMonitorHeart } from 'react-icons/md';
import { FiAlertTriangle } from 'react-icons/fi';

function App() {
  const [stats, setStats] = useState({ packets: 0, threats: 0, devices: 0, iotDevices: 0 });
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'devices', 'alerts'

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const flowsRes = await fetch('http://localhost:8000/api/flows');
        const flows = await flowsRes.json();
        const totalPackets = flows.reduce((sum, flow) => sum + flow.pkt_count, 0);
        const uniqueDevices = new Set(flows.map(flow => flow.key.split('->')[0])).size;

        const alertsRes = await fetch('http://localhost:8000/api/alerts');
        const alertsData = await alertsRes.json();

        // Fetch IoT device count
        let iotDeviceCount = 0;
        try {
          const iotRes = await fetch('http://localhost:8000/api/iot/summary');
          if (iotRes.ok) {
            const iotData = await iotRes.json();
            iotDeviceCount = iotData.iot_devices || 0;
          }
        } catch (err) {
          console.error('IoT devices not available:', err);
        }

        setStats({
          packets: totalPackets,
          threats: alertsData.total || 0,
          devices: uniqueDevices,
          iotDevices: iotDeviceCount
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
        <h2 className="text-green-500 text-center text-xl font-bold mb-6">UCS</h2>
        <ul className="list-none p-0">
          <li
            onClick={() => setActiveTab('dashboard')}
            className={`p-2.5 m-2 rounded-md cursor-pointer transition-colors ${
              activeTab === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-blue-600'
            }`}
          >
            <div className='flex items-center gap-2'><MdOutlineMonitorHeart fill='lightgreen' size={'50px'} /> <span>Dashboard</span></div>
          </li>
          <li
            onClick={() => setActiveTab('devices')}
            className={`p-2.5 m-2 rounded-md cursor-pointer transition-colors ${
              activeTab === 'devices' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-blue-600'
            }`}
          >
           <div className='flex items-center gap-2'><LuRadioTower fill='black' size={'50px'} /> <span>IoT Devices </span></div>
            {stats.iotDevices > 0 && (
              <span className="ml-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                {stats.iotDevices}
              </span>
            )}
          </li>
          <li
            onClick={() => setActiveTab('alerts')}
            className={`p-2.5 m-2 rounded-md cursor-pointer transition-colors ${
              activeTab === 'alerts' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-blue-600'
            }`}
          >
           <div className='flex items-center gap-2'><FiAlertTriangle fill='red' size={'50px'} /> <span> Alerts</span></div>
            {stats.threats > 0 && (
              <span className="ml-2 bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                {stats.threats}
              </span>
            )}
          </li>
        </ul>
      </aside>

      {/* Main content */}
      <div className="ml-60 flex-1 p-8">
        <header className="text-center mb-8">
          <h1 className="text-green-500 text-3xl font-bold">Unified Cybersecurity System</h1>
          <p className="text-lg">Threat Detection & IoT Security</p>
        </header>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <>
          {/*  
            <section className="flex gap-6 mb-8">
              <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40">
                <h3 className="mb-4 text-xl font-semibold">Total Packets</h3>
                <p className="text-2xl font-bold">{stats.packets}</p>
              </div>
              <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40 border-l-4 border-red-500">
                <h3 className="mb-4 text-xl font-semibold">Detected Threats</h3>
                <p className="text-2xl font-bold">{stats.threats}</p>
              </div>
              <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40 border-l-4 border-green-500">
                <h3 className="mb-4 text-xl font-semibold">Active Devices</h3>
                <p className="text-2xl font-bold">{stats.devices}</p>
              </div>
              <div className="flex-1 bg-slate-800 p-6 rounded-xl text-center shadow-lg shadow-black/40 border-l-4 border-blue-500">
                <h3 className="mb-4 text-xl font-semibold">IoT Devices</h3>
                <p className="text-2xl font-bold">{stats.iotDevices}</p>
              </div>
            </section>
            */}

            <section className="bg-slate-800 p-6 rounded-xl mb-8">
              <h2 className="text-xl font-semibold mb-4">Traffic Overview</h2>
              <Flows />
            </section>

            <section className="bg-slate-800 p-6 rounded-xl mb-8">
              <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
              <Alerts />
            </section>
          </>
        )}

        {/* IoT Devices Tab */}
        {activeTab === 'devices' && (
          <section className="bg-slate-800 p-6 rounded-xl mb-8">
            <h2 className="text-xl flex items-center gap-2 font-semibold mb-4"><LuRadioTower fill='black' size={'50px'} /> IoT Device Detection</h2>
            <IoTDevices />
          </section>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <section className="bg-slate-800 p-6 rounded-xl mb-8">
            <h2 className="text-xl font-semibold mb-4">Security Alerts</h2>
            <Alerts />
          </section>
        )}

        <footer className="text-center mt-4 p-4 bg-slate-800 rounded-lg">
          <p>© 2025 Unified Cybersecurity System | Project</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
