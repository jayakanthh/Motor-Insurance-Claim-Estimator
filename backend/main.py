import os
import sys
import json
import subprocess
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import Response
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Adjust path to include backend root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core import ClaimEstimator
from app.vision_model import VisionAgent
from app.pdf_export import build_estimate_pdf

app = FastAPI(title="Motor Insurance Claim Estimator API", version="1.0.0")

# CORS configuration
origins = [
    "http://localhost:5173",  # React default port
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    status: str
    data: dict


class ExportPdfRequest(BaseModel):
    report: dict

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/providers")
async def get_providers():
    """
    Returns a list of available AI providers and models.
    """
    providers = [
        {"id": "mock", "name": "Mock (Demo Mode)"},
        {"id": "openai", "name": "OpenAI GPT-4o"},
        {"id": "gemini", "name": "Gemini 1.5 Pro"}
    ]
    
    try:
        cp = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if cp.returncode == 0:
            lines = [ln.strip() for ln in (cp.stdout or "").splitlines() if ln.strip()]
            if len(lines) > 1:
                for ln in lines[1:]:
                    parts = ln.split()
                    if not parts:
                        continue
                    name = parts[0]
                    providers.append({
                        "id": f"ollama:{name}",
                        "name": f"Ollama ({name})",
                    })
    except Exception as e:
        print(f"Warning: Could not list Ollama models: {e}")

    return {"providers": providers}

@app.post("/api/analyze-claim")
async def analyze_claim(
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    extra: List[UploadFile] = File(default=[]),
    provider: str = Form("mock"),
    api_key: Optional[str] = Form(None),
    registration_number: Optional[str] = Form(None),
    detection_mode: str = Form("conservative"),
    labor_rate: float = Form(75.0)
):
    try:
        # Read image contents
        images_content = []
        
        # Mandatory images
        images_content.append(await front.read())
        images_content.append(await back.read())
        images_content.append(await left.read())
        images_content.append(await right.read())
        
        # Optional images
        for img in extra:
            images_content.append(await img.read())
        
        # Determine API Key
        # Priority: 1. Frontend provided 2. Env var
        final_api_key = api_key
        if not final_api_key:
            if provider == "openai":
                final_api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "gemini":
                final_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            elif provider == "ollama":
                final_api_key = "ollama" # Dummy key to pass check
        
        # Initialize Estimator
        estimator = ClaimEstimator(
            parts_db_path="data/parts_db.json", # Relative to project root
            labor_rate=labor_rate,
            provider=provider,
            api_key=final_api_key
        )
        
        # Run analysis with list of images
        result = estimator.analyze_claim(
            images_content,
            registration_number=registration_number,
            detection_mode=detection_mode,
        )
        
        if "error" in result:
            status_code = 400 if "Registration number is required" in str(result["error"]) else 500
            raise HTTPException(status_code=status_code, detail=result["error"])
            
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export-pdf")
async def export_pdf(payload: ExportPdfRequest):
    try:
        pdf_bytes = build_estimate_pdf(payload.report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=estimate.pdf"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
