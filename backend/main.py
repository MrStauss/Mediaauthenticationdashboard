# backend/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import uuid
import shutil
from pathlib import Path
import asyncio
from datetime import datetime

app = FastAPI(
    title="Media Authentication API",
    description="AI-powered media forensics and authentication",
    version="1.0.0"
)

# CORS for your Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage setup
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models matching your frontend
class AnalysisResult(BaseModel):
    id: str
    filename: str
    status: str  # "pending", "processing", "completed", "failed"
    trust_score: float  # 0-100
    verdict: str  # "authentic", "suspicious", "manipulated", "uncertain"
    confidence: str  # "high", "medium", "low"
    metadata_score: float
    forensic_score: float
    physics_score: Optional[float]
    details: Dict[str, Any]
    created_at: str
    processing_time: Optional[float]

# In-memory storage (replace with Supabase/PostgreSQL in production)
analysis_db: Dict[str, AnalysisResult] = {}

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_media(file: UploadFile = File(...)):
    """
    Main endpoint for media analysis
    Accepts: image/jpeg, image/png, image/webp, video/mp4
    """
    analysis_id = str(uuid.uuid4())[:12]
    timestamp = datetime.utcnow().isoformat()
    
    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/webp", "video/mp4"}
    if file.content_type not in allowed_types:
        raise HTTPException(400, detail=f"Unsupported file type: {file.content_type}")
    
    # Save file
    file_ext = file.filename.split('.')[-1]
    file_path = UPLOAD_DIR / f"{analysis_id}.{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create initial record
    result = AnalysisResult(
        id=analysis_id,
        filename=file.filename,
        status="processing",
        trust_score=0.0,
        verdict="pending",
        confidence="low",
        metadata_score=0.0,
        forensic_score=0.0,
        physics_score=None,
        details={"message": "Analysis started"},
        created_at=timestamp,
        processing_time=None
    )
    analysis_db[analysis_id] = result
    
    # Trigger async analysis (in production, use Celery/Redis)
    asyncio.create_task(process_analysis(analysis_id, file_path, file.content_type))
    
    return result

@app.get("/result/{analysis_id}", response_model=AnalysisResult)
async def get_result(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_db:
        raise HTTPException(404, detail="Analysis not found")
    return analysis_db[analysis_id]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

async def process_analysis(analysis_id: str, file_path: Path, content_type: str):
    """
    Background analysis task
    Replace with actual ML models in production
    """
    start_time = datetime.utcnow()
    result = analysis_db[analysis_id]
    
    try:
        # Simulate processing stages
        await asyncio.sleep(1)  # Metadata extraction
        
        # Mock scoring (replace with real analysis)
        import random
        metadata_score = random.uniform(0.6, 0.95)
        forensic_score = random.uniform(0.4, 0.9)
        
        # Calculate weighted trust score
        trust_score = (metadata_score * 0.3) + (forensic_score * 0.7)
        
        # Determine verdict
        if trust_score >= 0.8:
            verdict = "authentic"
            confidence = "high"
        elif trust_score >= 0.6:
            verdict = "likely_authentic"
            confidence = "medium"
        elif trust_score >= 0.4:
            verdict = "uncertain"
            confidence = "low"
        else:
            verdict = "manipulated"
            confidence = "high"
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update result
        result.status = "completed"
        result.trust_score = round(trust_score * 100, 1)
        result.verdict = verdict
        result.confidence = confidence
        result.metadata_score = round(metadata_score * 100, 1)
        result.forensic_score = round(forensic_score * 100, 1)
        result.processing_time = processing_time
        result.details = {
            "file_type": content_type,
            "file_size": file_path.stat().st_size,
            "metadata": {
                "camera": "iPhone 14 Pro" if random.random() > 0.5 else None,
                "software": None if random.random() > 0.3 else "Adobe Photoshop",
                "c2pa": random.random() > 0.7
            },
            "forensic": {
                "noise_consistency": round(random.uniform(0.7, 0.99), 2),
                "compression_artifacts": round(random.uniform(0.1, 0.5), 2),
                "ela_score": round(random.uniform(0.2, 0.8), 2)
            }
        }
        
    except Exception as e:
        result.status = "failed"
        result.details = {"error": str(e)}
    
    analysis_db[analysis_id] = result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
