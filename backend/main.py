import os
import sys
import json
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Adjust path to include backend root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core import ClaimEstimator
from app.vision_model import VisionAgent

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

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/analyze-claim")
async def analyze_claim(
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    left: UploadFile = File(...),
    right: UploadFile = File(...),
    extra: List[UploadFile] = File(default=[]),
    provider: str = Form("mock"),
    api_key: Optional[str] = Form(None),
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
        
        # Initialize Estimator
        estimator = ClaimEstimator(
            parts_db_path="data/parts_db.json", # Relative to project root
            labor_rate=labor_rate,
            provider=provider,
            api_key=api_key
        )
        
        # Run analysis with list of images
        result = estimator.analyze_claim(images_content)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
