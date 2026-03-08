import { CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';

interface Scan {
  id: string;
  filename: string;
  timestamp: string;
  verdict: 'authentic' | 'deepfake' | 'suspicious' | 'pending';
  confidenceScore: number;
  c2paDetected: boolean;
  dntFlag: boolean;
}

const mockScans: Scan[] = [
  {
    id: '1',
    filename: 'press_conference_2026.jpg',
    timestamp: '2 minutes ago',
    verdict: 'authentic',
    confidenceScore: 98,
    c2paDetected: true,
    dntFlag: true
  },
  {
    id: '2',
    filename: 'celebrity_interview.mp4',
    timestamp: '15 minutes ago',
    verdict: 'deepfake',
    confidenceScore: 94,
    c2paDetected: false,
    dntFlag: false
  },
  {
    id: '3',
    filename: 'news_broadcast.png',
    timestamp: '1 hour ago',
    verdict: 'authentic',
    confidenceScore: 96,
    c2paDetected: true,
    dntFlag: true
  },
  {
    id: '4',
    filename: 'social_media_post.jpg',
    timestamp: '2 hours ago',
    verdict: 'suspicious',
    confidenceScore: 67,
    c2paDetected: false,
    dntFlag: true
  },
  {
    id: '5',
    filename: 'viral_video.mp4',
    timestamp: '3 hours ago',
    verdict: 'deepfake',
    confidenceScore: 89,
    c2paDetected: false,
    dntFlag: false
  },
  {
    id: '6',
    filename: 'documentary_clip.mov',
    timestamp: '5 hours ago',
    verdict: 'authentic',
    confidenceScore: 97,
    c2paDetected: true,
    dntFlag: true
  }
];

export function RecentScans() {
  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'authentic':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'deepfake':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'suspicious':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return null;
    }
  };

  const getVerdictBadgeColor = (verdict: string) => {
    switch (verdict) {
      case 'authentic':
        return 'bg-green-100 text-green-700';
      case 'deepfake':
        return 'bg-red-100 text-red-700';
      case 'suspicious':
        return 'bg-yellow-100 text-yellow-700';
      case 'pending':
        return 'bg-gray-100 text-gray-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold mb-4">Recent Scans</h3>
      <div className="space-y-3">
        {mockScans.map((scan) => (
          <div
            key={scan.id}
            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center gap-4 flex-1">
              {getVerdictIcon(scan.verdict)}
              <div className="flex-1">
                <p className="font-medium text-gray-900">{scan.filename}</p>
                <p className="text-sm text-gray-500">{scan.timestamp}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right mr-2">
                <p className="text-sm font-semibold text-gray-700">{scan.confidenceScore}%</p>
                <div className="flex gap-1 mt-1">
                  {scan.c2paDetected && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">C2PA</span>
                  )}
                  {scan.dntFlag && (
                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">DNT</span>
                  )}
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${getVerdictBadgeColor(scan.verdict)}`}>
                {scan.verdict}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
