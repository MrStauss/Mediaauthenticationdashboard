import { useState } from 'react';
import { 
  Upload, 
  Shield, 
  Microscope, 
  Brain, 
  FileCheck, 
  ChevronDown,
  ChevronUp,
  Check,
  X,
  AlertTriangle
} from 'lucide-react';

interface Phase {
  id: number;
  emoji: string;
  title: string;
  subtitle: string;
  icon: any;
  color: string;
  bgColor: string;
  checks: {
    name: string;
    description: string;
    status?: 'pass' | 'fail' | 'warning';
  }[];
}

const phases: Phase[] = [
  {
    id: 1,
    emoji: '📥',
    title: 'Input Trigger',
    subtitle: 'File Reception & Validation',
    icon: Upload,
    color: 'text-blue-600',
    bgColor: 'bg-blue-500',
    checks: [
      { name: 'User forwards file to WhatsApp Bot', description: 'Video, photo, or audio file received' },
      { name: 'Acknowledge receipt', description: '🔍 Analyzing... message sent to manage latency expectations' },
      { name: 'Format validation', description: 'Supported formats: JPG, PNG, MP4, MOV, WAV', status: 'pass' }
    ]
  },
  {
    id: 2,
    emoji: '🛡️',
    title: 'Truth Layer',
    subtitle: 'Metadata & Provenance',
    icon: Shield,
    color: 'text-purple-600',
    bgColor: 'bg-purple-500',
    checks: [
      { name: 'C2PA Manifest Check', description: 'Extract Content Credentials if present', status: 'pass' },
      { name: 'Camera signatures', description: 'Check for Sony/Leica/Nikon authentication', status: 'pass' },
      { name: 'AI signatures', description: 'Scan for OpenAI/Adobe markers', status: 'pass' },
      { name: 'DNT Flag Check', description: 'Scan for "Do Not Train" metadata or SynthID watermarks', status: 'warning' }
    ]
  },
  {
    id: 3,
    emoji: '🔬',
    title: 'Forensic Layer',
    subtitle: 'Deep Analysis',
    icon: Microscope,
    color: 'text-green-600',
    bgColor: 'bg-green-500',
    checks: [
      { name: 'Pixel-level CNNs', description: 'Detect frequency artifacts in image data', status: 'pass' },
      { name: 'Semantic VLM (FakeVLM)', description: 'Verify physics: shadows, reflections, lighting', status: 'pass' },
      { name: 'Frame Sampling (Video)', description: 'Analyze 5 keyframes at high resolution', status: 'pass' },
      { name: 'R-PPG Biological Check', description: 'Remote Pulse Detection for human heartbeat', status: 'pass' },
      { name: 'Audio Vocoder Analysis', description: 'Check for AI voice clone artifacts', status: 'pass' }
    ]
  },
  {
    id: 4,
    emoji: '📊',
    title: 'Decision Engine',
    subtitle: 'Weighted Scoring',
    icon: Brain,
    color: 'text-orange-600',
    bgColor: 'bg-orange-500',
    checks: [
      { name: 'C2PA Signed', description: '+50 Trust Score', status: 'pass' },
      { name: 'No Pixel Artifacts', description: '+30 Trust Score', status: 'pass' },
      { name: 'Logical Shadows', description: '+20 Trust Score', status: 'pass' },
      { name: 'Final Trust Score', description: '99% Authentic - High Confidence' }
    ]
  },
  {
    id: 5,
    emoji: '📤',
    title: 'Output',
    subtitle: 'Verdict Card',
    icon: FileCheck,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-500',
    checks: [
      { name: 'Send Verdict Card', description: 'Formatted result with visual indicators' },
      { name: 'Explainability', description: 'Show specific findings and confidence factors' },
      { name: 'Call to Action', description: '"Report this fake" or "Secure your media with DNT tag"' }
    ]
  }
];

export function DetailedPhaseFlow() {
  const [expandedPhase, setExpandedPhase] = useState<number | null>(1);

  const togglePhase = (phaseId: number) => {
    setExpandedPhase(expandedPhase === phaseId ? null : phaseId);
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'pass':
        return <Check className="w-4 h-4 text-green-600" />;
      case 'fail':
        return <X className="w-4 h-4 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold mb-6">5-Phase Authentication Process</h3>
      
      <div className="space-y-4">
        {phases.map((phase, index) => (
          <div key={phase.id}>
            {/* Phase Header */}
            <div
              onClick={() => togglePhase(phase.id)}
              className="cursor-pointer bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`${phase.bgColor} w-12 h-12 rounded-lg flex items-center justify-center shadow-md`}>
                    <phase.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{phase.emoji}</span>
                      <h4 className="font-semibold text-gray-900">Phase {phase.id}: {phase.title}</h4>
                    </div>
                    <p className="text-sm text-gray-600">{phase.subtitle}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500 font-medium">{phase.checks.length} checks</span>
                  {expandedPhase === phase.id ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </div>
              </div>
            </div>

            {/* Phase Details */}
            {expandedPhase === phase.id && (
              <div className="mt-2 ml-16 mr-4 space-y-2">
                {phase.checks.map((check, checkIndex) => (
                  <div
                    key={checkIndex}
                    className="flex items-start gap-3 p-3 bg-white border border-gray-200 rounded-lg"
                  >
                    <div className="mt-0.5">
                      {getStatusIcon(check.status)}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-sm text-gray-900">{check.name}</p>
                      <p className="text-xs text-gray-600 mt-0.5">{check.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Connector Arrow */}
            {index < phases.length - 1 && (
              <div className="flex justify-center my-2">
                <div className="w-0.5 h-6 bg-gray-300"></div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
