# Instant Motor-Claim Estimator

An intelligent agent that analyzes car damage photos and provides 'Pre-Approval' cost estimates for repairs using Computer Vision and Vision LLMs.

## Project Overview

This project aims to streamline the motor insurance claim process by automating damage assessment and cost estimation. The system leverages state-of-the-art Vision Language Models (VLMs) to identify vehicle damage from images and generate detailed repair cost estimates.

## Key Objectives

- **Accurate Analysis**: Identify damaged parts with high precision using Vision LLMs (GPT-4o, Gemini, or Local Ollama/LLaVA).
- **Instant Estimates**: Provide immediate labor and part cost calculations.
- **Real-Time Pricing**: Fetches current market prices for car parts in India (INR) using web search.
- **Efficiency**: Reduce claim processing time significantly.
- **User Experience**: Improve customer satisfaction with quick feedback.

## Tech Stack

- **Frontend**: React, Tailwind CSS
- **Backend**: FastAPI (Python)
- **AI/ML**: 
    - **OpenAI GPT-4o** / **Google Gemini** (Cloud Vision LLMs)
    - **Ollama (LLaVA)** (Local Vision LLM support)
    - **OpenCV** (Image pre-processing)
- **Data Handling**: Pandas, JSON
- **Search**: DuckDuckGo Search (for real-time part pricing)

## Features

1. **Image Upload**: Interface for users to upload car damage photos (Front, Back, Left, Right + Extras).
2. **Damage Detection**: Automated identification of scratches, dents, broken glass, etc.
3. **Car Identification**: Attempts to identify Car Make and Model for accurate pricing.
4. **Real-Time Cost Estimation**: Web search integration to find current part prices in INR.
5. **Report Generation**: Detailed breakdown of the estimate including labor and taxes (GST).

## Setup Instructions

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Install Ollama (optional for local use): [https://ollama.com/](https://ollama.com/) and pull model: `ollama pull llava:7b`
4. Run server: `uvicorn main:app --reload`

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`

## Deliverables

- [x] Technical Documentation
- [x] Working Prototype (Full Stack)
- [x] Damage Detection Model (via VLM)
- [x] Cost Estimation Report (INR currency)
- [x] Real-time Web Search Integration
