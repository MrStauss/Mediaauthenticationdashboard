// src/components/AnalysisResults.tsx
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Shield, FileSearch } from 'lucide-react';
import { pollForResults, AnalysisResponse } from '@/services/api';

interface AnalysisResultsProps {
  analysisId: string;
}

export function AnalysisResults({ analysisId }: AnalysisResultsProps) {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    pollForResults(analysisId, (update) => {
      setResult(update);
      setLoading(update.status === 'processing');
    });
  }, [analysisId]);

  if (loading || !result) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
            <p>Analyzing media... {result?.status === 'processing' && '(Processing)'}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'authentic': return 'bg-green-500';
      case 'likely_authentic': return 'bg-green-400';
      case 'uncertain': return 'bg-yellow-500';
      case 'likely_manipulated': return 'bg-orange-500';
      case 'manipulated': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Trust Score Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Trust Score</span>
            <Badge className={getVerdictColor(result.verdict)}>
              {result.verdict.replace('_', ' ').toUpperCase()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold mb-2">{result.trust_score}/100</div>
          <Progress value={result.trust_score} className="h-2" />
          <p className="text-sm text-muted-foreground mt-2">
            Confidence: {result.confidence}
          </p>
        </CardContent>
      </Card>

      {/* Component Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard
          title="Metadata"
          score={result.metadata_score}
          icon={<FileSearch className="h-4 w-4" />}
          details={result.details.metadata}
        />
        <ScoreCard
          title="Forensic"
          score={result.forensic_score}
          icon={<Shield className="h-4 w-4" />}
          details={result.details.forensic}
        />
        <ScoreCard
          title="Physics"
          score={result.physics_score || 0}
          icon={<AlertCircle className="h-4 w-4" />}
          details={null}
        />
      </div>

      {/* Technical Details */}
      {result.details.forensic && (
        <Card>
          <CardHeader>
            <CardTitle>Forensic Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span>Noise Consistency</span>
              <span>{(result.details.forensic.noise_consistency * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span>Compression Artifacts</span>
              <span>{(result.details.forensic.compression_artifacts * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span>ELA Score</span>
              <span>{(result.details.forensic.ela_score * 100).toFixed(1)}%</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ScoreCard({ title, score, icon, details }: {
  title: string;
  score: number;
  icon: React.ReactNode;
  details: any;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{score.toFixed(1)}%</div>
        {details?.camera && (
          <p className="text-xs text-muted-foreground mt-1">
            Camera: {details.camera}
          </p>
        )}
        {details?.software && (
          <p className="text-xs text-red-500 mt-1">
            Edited with: {details.software}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
