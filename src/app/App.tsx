import { Shield, Activity, FileSearch } from 'lucide-react';
import { DetailedPhaseFlow } from './components/DetailedPhaseFlow';
import { RecentScans } from './components/RecentScans';
import { DeepfakeTrends } from './components/DeepfakeTrends';
import { VerdictCard } from './components/VerdictCard';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MediaAuth Dashboard</h1>
                <p className="text-sm text-gray-600">Real-time media authentication monitoring</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-green-100 px-3 py-2 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">System Online</span>
              </div>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                New Scan
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <FileSearch className="w-6 h-6 opacity-80" />
              <p className="text-sm font-medium opacity-90">Scans This Week</p>
            </div>
            <p className="text-4xl font-bold">1,247</p>
            <p className="text-sm opacity-80 mt-2">↑ 18% from last week</p>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-6 h-6 opacity-80" />
              <p className="text-sm font-medium opacity-90">Deepfake Rate</p>
            </div>
            <p className="text-4xl font-bold">13.2%</p>
            <p className="text-sm opacity-80 mt-2">↓ 2.1% from last week</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-6 h-6 opacity-80" />
              <p className="text-sm font-medium opacity-90">C2PA Detection Rate</p>
            </div>
            <p className="text-4xl font-bold">68%</p>
            <p className="text-sm opacity-80 mt-2">↑ 5% from last week</p>
          </div>
        </div>

        {/* Logic Flow Diagram */}
        <DetailedPhaseFlow />

        {/* Charts and Analytics */}
        <DeepfakeTrends />

        {/* Recent Scans */}
        <RecentScans />

        {/* Verdict Card Examples */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold mb-6">Sample Verdict Cards</h3>
          <div className="grid grid-cols-3 gap-6">
            <VerdictCard type="authentic" />
            <VerdictCard type="deepfake" />
            <VerdictCard type="suspicious" />
          </div>
        </div>
      </main>
    </div>
  );
}