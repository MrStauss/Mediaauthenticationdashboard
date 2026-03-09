from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import uuid
import shutil
import json
from pathlib import Path
import asyncio
from datetime import datetime
import os
import httpx
from dotenv import load_dotenv

# New Imports for Provenance and Messaging
import c2pa
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

app = FastAPI(
    title="Media Authentication API",
    description="AI-powered media forensics and authentication",
    version="1.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class AnalysisResult(BaseModel):
    id: str
    filename: str
    status: str 
    trust_score: float  
    verdict: str  
    confidence: str  
    metadata_score: float
    forensic_score: float
    details: Dict[str, Any]
    created_at: str

analysis_db: Dict[str, AnalysisResult] = {}

# --- HELPER: C2PA TRUTH LAYER ---
def verify_c2pa_provenance(file_path: Path):
    try:
        reader = c2pa.Reader.from_file(str(file_path))
        manifest = reader.get_active_manifest()
        is_ai = any(a['label'] == 'c2pa.ai_generated' for a in manifest.v1_manifest.get('assertions', []))
        return {
            "exists": True,
            "issuer": manifest.v1_manifest.get("signature_info", {}).get("issuer"),
            "is_ai_declared": is_ai,
            "score": 100 if not is_ai else 50
        }
    except Exception:
        return {"exists": False, "score": 0}

# --- BACKGROUND PROCESSOR ---
async def process_analysis(analysis_id: str, file_path: Path, to_number: Optional[str] = None):
    """The 5-Phase Decision Engine with Proactive Messaging"""
    result = analysis_db[analysis_id]
    
    # Phase 2: Truth Layer (C2PA)
    c2pa_data = verify_c2pa_provenance(file_path)
    metadata_score = c2pa_data["score"]

    # Phase 3: Forensic Layer (Mocked for Prototype)
    await asyncio.sleep(3) # Simulating heavy AI processing
    forensic_score = 85.0 

    # Phase 4: Weighted Scoring
    if c2pa_data["exists"]:
        trust_score = (metadata_score * 0.6) + (forensic_score * 0.4)
    else:
        trust_score = forensic_score

    # Determine Verdict
    if trust_score > 80: verdict, conf = "authentic", "high"
    elif trust_score > 50: verdict, conf = "suspicious", "medium"
    else: verdict, conf = "manipulated", "high"

    # Update DB
    result.status = "completed"
    result.trust_score = trust_score
    result.verdict = verdict
    result.confidence = conf
    result.metadata_score = metadata_score
    result.forensic_score = forensic_score
    result.details = {
        "c2pa_present": c2pa_data["exists"],
        "issuer": c2pa_data.get("issuer", "None"),
        "forensic_findings": "No significant pixel anomalies detected."
    }
    analysis_db[analysis_id] = result

    # Phase 5: Proactive WhatsApp Notification
    if to_number and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            emoji = "✅" if verdict == "authentic" else "🚨" if verdict == "manipulated" else "⚠️"
            
            message_body = (
                f"{emoji} *Media Analysis Complete*\n\n"
                f"*Verdict:* {verdict.upper()}\n"
                f"*Trust Score:* {int(trust_score)}%\n"
                f"*Confidence:* {conf}\n\n"
                f"View your dashboard for details."
            )
            
            client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=message_body,
                to=to_number
            )
        except Exception as e:
            print(f"Failed to send proactive WhatsApp: {e}")

# --- ENDPOINTS ---
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    media_url = form_data.get('MediaUrl0')
    from_number = form_data.get('From')

    response = MessagingResponse()
    
    if media_url:
        analysis_id = str(uuid.uuid4())[:12]
        file_path = UPLOAD_DIR / f"{analysis_id}.jpg"
        
        async with httpx.AsyncClient() as client:
            media_resp = await client.get(media_url)
            if media_resp.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(media_resp.content)
                
                analysis_db[analysis_id] = AnalysisResult(
                    id=analysis_id, filename=f"whatsapp_{analysis_id}.jpg", 
                    status="processing", trust_score=0.0, verdict="pending", 
                    confidence="low", metadata_score=0.0, forensic_score=0.0, 
                    details={}, created_at=datetime.utcnow().isoformat()
                )
                
                # Pass from_number to ensure the bot can reply back
                asyncio.create_task(process_analysis(analysis_id, file_path, from_number))
                
                response.message("🔍 Analysis started! I'll check the metadata and forensic patterns. I'll text you the verdict shortly.")
            else:
                response.message("❌ I couldn't download the media. Please try again.")
    else:
        response.message("👋 Send me a photo, and I'll tell you if it's AI-doctored!")

    return str(response)

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_media(file: UploadFile = File(...)):
    analysis_id = str(uuid.uuid4())[:12]
    file_ext = file.filename.split('.')[-1]
    file_path = UPLOAD_DIR / f"{analysis_id}.{file_ext}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    result = AnalysisResult(
        id=analysis_id, filename=file.filename, status="processing",
        trust_score=0.0, verdict="pending", confidence="low",
        metadata_score=0.0, forensic_score=0.0,
        details={"message": "Processing via Dashboard..."},
        created_at=datetime.utcnow().isoformat()
    )
    analysis_db[analysis_id] = result
    asyncio.create_task(process_analysis(analysis_id, file_path))
    
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
