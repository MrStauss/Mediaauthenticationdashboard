import { CheckCircle, XCircle, AlertTriangle, Shield, Eye, Zap, Flag } from 'lucide-react';

interface VerdictCardProps {
  type?: 'authentic' | 'deepfake' | 'suspicious';
}

export function VerdictCard({ type = 'authentic' }: VerdictCardProps) {
  const verdictConfig = {
    authentic: {
      icon: CheckCircle,
      title: 'AUTHENTIC',
      subtitle: 'This media appears to be genuine',
      color: 'green',
      bgGradient: 'from-green-500 to-green-600',
      score: 99,
      findings: [
        { icon: Shield, text: 'C2PA signature verified from Sony camera', positive: true },
        { icon: Eye, text: 'No pixel-level artifacts detected', positive: true },
        { icon: Zap, text: 'Lighting and shadows are physically consistent', positive: true },
        { icon: Flag, text: '"Do Not Train" flag detected and honored', positive: true }
      ],
      action: 'Secure your own media with a DNT tag',
      actionColor: 'bg-green-600 hover:bg-green-700'
    },
    deepfake: {
      icon: XCircle,
      title: 'DEEPFAKE DETECTED',
      subtitle: 'This media shows signs of manipulation',
      color: 'red',
      bgGradient: 'from-red-500 to-red-600',
      score: 12,
      findings: [
        { icon: Shield, text: 'No C2PA metadata found', positive: false },
        { icon: Eye, text: 'Found 3 inconsistencies in the lighting of the eyes', positive: false },
        { icon: Zap, text: 'Repeated pixel patterns detected in face region', positive: false },
        { icon: Flag, text: 'Blurred ear geometry typical of AI generation', positive: false }
      ],
      action: 'Report this fake',
      actionColor: 'bg-red-600 hover:bg-red-700'
    },
    suspicious: {
      icon: AlertTriangle,
      title: 'SUSPICIOUS',
      subtitle: 'Unable to verify authenticity',
      color: 'yellow',
      bgGradient: 'from-yellow-500 to-yellow-600',
      score: 67,
      findings: [
        { icon: Shield, text: 'No C2PA signature present', positive: false },
        { icon: Eye, text: 'Minor compression artifacts detected', positive: false },
        { icon: Zap, text: 'Physics analysis: inconclusive', positive: null },
        { icon: Flag, text: 'File metadata suggests heavy editing', positive: false }
      ],
      action: 'Request source verification',
      actionColor: 'bg-yellow-600 hover:bg-yellow-700'
    }
  };

  const config = verdictConfig[type];
  const VerdictIcon = config.icon;

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-lg max-w-md">
      {/* Header with gradient */}
      <div className={`bg-gradient-to-r ${config.bgGradient} p-6 text-white`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <VerdictIcon className="w-8 h-8" />
            <div>
              <h3 className="text-2xl font-bold">{config.title}</h3>
              <p className="text-sm opacity-90">{config.subtitle}</p>
            </div>
          </div>
        </div>
        
        {/* Trust Score */}
        <div className="bg-white/20 backdrop-blur-sm rounded-lg p-4 mt-4">
          <div className="flex items-end justify-between">
            <div>
              <p className="text-xs opacity-80 uppercase tracking-wide">Trust Score</p>
              <p className="text-5xl font-bold mt-1">{config.score}%</p>
            </div>
            <div className="w-24 h-24 relative">
              <svg className="transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="rgba(255,255,255,0.2)"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  stroke="white"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${config.score * 2.51} 251`}
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Findings */}
      <div className="p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Analysis Findings</h4>
        <div className="space-y-3">
          {config.findings.map((finding, index) => (
            <div key={index} className="flex items-start gap-3">
              <div className={`mt-0.5 ${
                finding.positive === true ? 'text-green-600' : 
                finding.positive === false ? 'text-red-600' : 
                'text-gray-400'
              }`}>
                <finding.icon className="w-5 h-5" />
              </div>
              <p className="text-sm text-gray-700 flex-1">{finding.text}</p>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <button className={`w-full mt-6 ${config.actionColor} text-white font-medium py-3 rounded-lg transition-colors`}>
          {config.action}
        </button>

        {/* Footer */}
        <p className="text-xs text-gray-500 text-center mt-4">
          Analyzed on {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
