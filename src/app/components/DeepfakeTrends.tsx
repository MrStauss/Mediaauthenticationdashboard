import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';

const weeklyData = [
  { day: 'Mon', authentic: 145, deepfake: 23, suspicious: 12 },
  { day: 'Tue', authentic: 167, deepfake: 31, suspicious: 18 },
  { day: 'Wed', authentic: 134, deepfake: 28, suspicious: 15 },
  { day: 'Thu', authentic: 189, deepfake: 42, suspicious: 21 },
  { day: 'Fri', authentic: 201, deepfake: 38, suspicious: 19 },
  { day: 'Sat', authentic: 176, deepfake: 35, suspicious: 16 },
  { day: 'Sun', authentic: 158, deepfake: 29, suspicious: 14 }
];

const detectionMethodData = [
  { id: 'c2pa', name: 'C2PA Metadata', value: 45 },
  { id: 'pixel', name: 'Pixel Analysis', value: 35 },
  { id: 'dnt', name: 'DNT Flags', value: 12 },
  { id: 'combined', name: 'Combined Analysis', value: 8 }
];

const COLORS = ['#8b5cf6', '#06b6d4', '#f59e0b', '#10b981'];

export function DeepfakeTrends() {
  return (
    <div className="space-y-6">
      {/* Weekly Trend Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Weekly Scan Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={weeklyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="day" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#ffffff', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px'
              }}
            />
            <Area type="monotone" dataKey="authentic" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.6} />
            <Area type="monotone" dataKey="suspicious" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} />
            <Area type="monotone" dataKey="deepfake" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Detection Method Distribution */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-4">Detection Methods</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={detectionMethodData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {detectionMethodData.map((entry, index) => (
                  <Cell key={entry.id} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Stats Cards */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Scans Today</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">324</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-green-600 mt-2">↑ 12% from yesterday</p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Deepfakes Detected</p>
                <p className="text-3xl font-bold text-red-600 mt-1">42</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-red-600 mt-2">13% of total scans</p>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Confidence Score</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">94.2%</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2">Excellent accuracy</p>
          </div>
        </div>
      </div>
    </div>
  );
}