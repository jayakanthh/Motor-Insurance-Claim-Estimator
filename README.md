# Instant Motor-Claim Estimator

An intelligent agent that analyzes car damage photos and provides 'Pre-Approval' cost estimates for repairs using Computer Vision and Vision LLMs.

## Project Overview

This project aims to streamline the motor insurance claim process by automating damage assessment and cost estimation. The system leverages state-of-the-art Vision Language Models (VLMs) to identify vehicle damage from images and generate detailed repair cost estimates.

## Key Objectives

- **Accurate Analysis**: Identify damaged parts with high precision.
- **Instant Estimates**: Provide immediate labor and part cost calculations.
- **Efficiency**: Reduce claim processing time significantly.
- **User Experience**: Improve customer satisfaction with quick feedback.

## Tech Stack

- **Frontend**: React, Tailwind CSS
- **Backend**: FastAPI (Python)
- **AI/ML**: 
    - OpenAI GPT-4o / Google Gemini 1.5 Pro (Vision LLM for damage assessment)
    - OpenCV (Image pre-processing)
- **Data Handling**: Pandas, JSON

## Features

1. **Image Upload**: Interface for users to upload car damage photos.
2. **Damage Detection**: Automated identification of scratches, dents, broken glass, etc.
3. **Cost Estimation**: Logic engine to map damages to repair costs (parts + labor).
4. **Report Generation**: detailed breakdown of the estimate.

## Setup Instructions

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run server: `python main.py`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`

## Deliverables

- [x] Technical Documentation
- [x] Working Prototype (Full Stack)
- [x] Damage Detection Model (via VLM)
- [x] Cost Estimation Report
