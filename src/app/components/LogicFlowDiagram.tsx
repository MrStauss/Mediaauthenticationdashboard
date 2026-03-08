import { ArrowRight, Image, Shield, Scan, Flag, FileCheck } from 'lucide-react';

export function LogicFlowDiagram() {
  const steps = [
    { icon: Image, label: 'User sends image', color: 'bg-blue-500' },
    { icon: Shield, label: 'Bot checks C2PA metadata', color: 'bg-purple-500' },
    { icon: Scan, label: 'Bot runs pixel analysis', color: 'bg-green-500' },
    { icon: Flag, label: 'Bot checks "Do Not Train" flags', color: 'bg-orange-500' },
    { icon: FileCheck, label: 'Bot replies with Verdict Card', color: 'bg-indigo-500' }
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold mb-6">Authentication Logic Flow</h3>
      <div className="flex items-center justify-between gap-3 overflow-x-auto pb-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-3 flex-shrink-0">
            <div className="flex flex-col items-center gap-3 min-w-[140px]">
              <div className={`${step.color} w-16 h-16 rounded-xl flex items-center justify-center shadow-lg`}>
                <step.icon className="w-8 h-8 text-white" />
              </div>
              <p className="text-sm text-center text-gray-700 leading-tight">{step.label}</p>
            </div>
            {index < steps.length - 1 && (
              <ArrowRight className="w-6 h-6 text-gray-400 flex-shrink-0 mt-[-30px]" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
