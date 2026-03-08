// src/services/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  id: string;
  filename: string;
  status: string;
  trust_score: number;
  verdict: 'authentic' | 'suspicious' | 'manipulated' | 'uncertain';
  confidence: 'high' | 'medium' | 'low';
  metadata_score: number;
  forensic_score: number;
  physics_score?: number;
  details: {
    metadata?: {
      camera?: string;
      software?: string;
      c2pa?: boolean;
    };
    forensic?: {
      noise_consistency: number;
      compression_artifacts: number;
      ela_score: number;
    };
  };
  created_at: string;
  processing_time?: number;
}

export async function uploadMedia(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

export async function getAnalysisResult(id: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_URL}/result/${id}`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch results');
  }
  
  return response.json();
}

// Polling function for real-time updates
export async function pollForResults(
  id: string, 
  onUpdate: (result: AnalysisResponse) => void,
  interval: number = 2000
): Promise<void> {
  const checkStatus = async () => {
    try {
      const result = await getAnalysisResult(id);
      onUpdate(result);
      
      if (result.status === 'processing') {
        setTimeout(checkStatus, interval);
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  };
  
  checkStatus();
}
