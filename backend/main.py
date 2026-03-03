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
cors_origins_env = [
    o.strip()
    for o in (os.getenv("CORS_ORIGINS") or "").split(",")
    if o.strip()
]
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    *cors_origins_env,
]
origin_regex = os.getenv("CORS_ORIGIN_REGEX") or r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=False,
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
    Returns a list of available AI providers.
    Always exposes cloud providers; actual API key can be provided by the client.
    """
    providers = [
        {"id": "openai", "name": "OpenAI GPT-4o"},
        {"id": "gemini", "name": "Gemini 1.5 Pro"},
    ]
    return {"providers": providers}

class ValidateKeyRequest(BaseModel):
    provider: str
    api_key: str

@app.post("/api/validate-key")
async def validate_key(req: ValidateKeyRequest):
    """
    Validates an API key by making a lightweight test call to the provider.
    """
    try:
        if req.provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=req.api_key)
            # Minimal call to check key validity
            client.models.list()
            return {"valid": True}
        elif req.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=req.api_key)
            list(genai.list_models())
            return {"valid": True}
        else:
            return {"valid": False, "error": f"Unknown provider: {req.provider}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@app.post("/api/analyze-claim")
async def analyze_claim(
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    extra: List[UploadFile] = File(default=[]),
    provider: str = Form("gemini"),
    api_key: Optional[str] = Form(None),
    registration_number: Optional[str] = Form(None),
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
            detection_mode="conservative",
        )
        
        if "error" in result:
            error_text = str(result.get("error") or "Unknown error")
            error_type = result.get("error_type")

            if error_type == "invalid_api_key":
                raise HTTPException(
                    status_code=401,
                    detail={"message": error_text, "error_type": error_type},
                )

            status_code = 400 if "Registration number is required" in error_text else 500
            raise HTTPException(
                status_code=status_code,
                detail={"message": error_text, "error_type": error_type},
            )
            
        return {
            "status": "success",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "error_type": "server_error"})


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
