from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn, uuid, shutil, asyncio, os, httpx, json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import c2pa

# 1. Load Environment Variables
load_dotenv()

# Securely pull credentials from Railway Variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Corrected Template SID from your Twilio Content Builder
CONTENT_SID = "HXfe122e8432f88a666bcec5ba864b70a3" 

app = FastAPI(
    title="Media Authentication API",
    description="Full-stack prototype for AI media forensics",
    version="1.1.0"
)

# 2. CORS Configuration for your Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
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

# In-memory store (Postgres integration would replace this for persistence)
analysis_db: Dict[str, AnalysisResult] = {}

# --- PHASE 2: PROVENANCE (C2PA) ---
def verify_c2pa_provenance(file_path: Path):
    """Checks for cryptographic 'Content Credentials' as seen in Figma Phase 2"""
    try:
        reader = c2pa.Reader.from_file(str(file_path))
        manifest = reader.get_active_manifest()
        is_ai = any(a['label'] == 'c2pa.ai_generated' for a in manifest.v1_manifest.get('assertions', []))
        return {
            "exists": True, 
            "issuer": manifest.v1_manifest.get("signature_info", {}).get("issuer"), 
            "score": 100 if not is_ai else 50
        }
    except:
        return {"exists": False, "score": 0}

# --- PHASE 5: PROACTIVE TEMPLATE REPLY ---
async def process_analysis(analysis_id: str, file_path: Path, to_number: Optional[str] = None):
    """The Decision Engine that pushes results back to WhatsApp using Templates"""
    result = analysis_db[analysis_id]
    
    # 1. Run C2PA Check
    c2pa_data = verify_c2pa_provenance(file_path)
    
    # 2. Simulate Phase 3 Forensics
    await asyncio.sleep(4) 
    forensic_score = 88.0 
    
    # 3. Phase 4: Weighted Scoring
    if c2pa_data["exists"]:
        trust_score = (c2pa_data["score"] * 0.6) + (forensic_score * 0.4)
    else:
        trust_score = forensic_score
        
    verdict = "authentic" if trust_score > 80 else "manipulated"
    conf = "high" if abs(trust_score - 50) > 30 else "medium"

    # Update Database State
    result.status = "completed"
    result.trust_score = trust_score
    result.verdict = verdict
    result.confidence = conf
    result.metadata_score = c2pa_data["score"]
    result.forensic_score = forensic_score
    result.details = {"c2pa_issuer": c2pa_data.get("issuer", "N/A")}
    analysis_db[analysis_id] = result

    # 4. Push Template Result via Twilio
    if to_number and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Map variables to your approved template: {{1}}=Verdict, {{2}}=Score, {{3}}=URL
            content_vars = json.dumps({
                "1": verdict.upper(),
                "2": f"{int(trust_score)}%",
                "3": f"https://mediaauthenticationdashboard-production.up.railway.app/scans/{analysis_id}"
            })

            client.messages.create(
                from_=TWILIO_NUMBER,
                to=to_number,
                content_sid=CONTENT_SID,
                content_variables=content_vars
            )
        except Exception as e:
            print(f"Twilio Template Error: {e}")

# --- ENDPOINT: WHATSAPP WEBHOOK ---
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    media_url = form_data.get('MediaUrl0')
    from_number = form_data.get('From')
    
    tw_resp = MessagingResponse()
    if media_url:
        aid = str(uuid.uuid4())[:12]
        path = UPLOAD_DIR / f"{aid}.jpg"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(media_url)
            if resp.status_code == 200:
                with open(path, "wb") as f: f.write(resp.content)
                
                # Initialize analysis record
                analysis_db[aid] = AnalysisResult(
                    id=aid, filename=f"wa_{aid}.jpg", status="processing",
                    trust_score=0.0, verdict="pending", confidence="low",
                    metadata_score=0.0, forensic_score=0.0, details={},
                    created_at=datetime.utcnow().isoformat()
                )
                
                # Start Background Engine
                asyncio.create_task(process_analysis(aid, path, from_number))
                tw_resp.message("🔍 Media received. Verifying signatures and pixel patterns. I'll WhatsApp you the verdict shortly.")
            else:
                tw_resp.message("❌ Error downloading media. Please try again.")
    else:
        tw_resp.message("👋 Welcome! Send a photo or video to verify its authenticity.")
        
    return str(tw_resp)

# --- ENDPOINT: DASHBOARD UPLOAD ---
@app.post("/analyze", response_model=AnalysisResult)
async def analyze_media(file: UploadFile = File(...)):
    aid = str(uuid.uuid4())[:12]
    path = UPLOAD_DIR / f"{aid}_{file.filename}"
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = AnalysisResult(
        id=aid, filename=file.filename, status="processing",
        trust_score=0.0, verdict="pending", confidence="low",
        metadata_score=0.0, forensic_score=0.0, details={},
        created_at=datetime.utcnow().isoformat()
    )
    analysis_db[aid] = result
    asyncio.create_task(process_analysis(aid, path))
    return result

# --- ENDPOINT: GET INDIVIDUAL SCAN ---
@app.get("/scans/{scan_id}", response_model=AnalysisResult)
async def get_scan(scan_id: str):
    if scan_id not in analysis_db:
        raise HTTPException(status_code=404, detail="Scan not found")
    return analysis_db[scan_id]

if __name__ == "__main__":
    # Railway automatically sets the PORT environment variable
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
