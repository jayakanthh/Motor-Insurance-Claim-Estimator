import os
import sys
import json
from typing import Optional
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
    image: UploadFile = File(...),
    provider: str = Form("mock"),
    api_key: Optional[str] = Form(None),
    labor_rate: float = Form(75.0)
):
    try:
        # Read image content
        contents = await image.read()
        
        # Initialize Estimator
        # Note: In a production app, we might want to dependency inject this or cache it
        # But for now, re-initializing is fine as it's lightweight
        estimator = ClaimEstimator(
            parts_db_path="data/parts_db.json", # Relative to project root
            labor_rate=labor_rate,
            provider=provider,
            api_key=api_key
        )
        
        # Run analysis
        result = estimator.analyze_claim(contents)
        
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
