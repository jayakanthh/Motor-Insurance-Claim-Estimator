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

- **Frontend**: Streamlit (for rapid prototyping and interactive UI)
- **Backend**: Python
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

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (API keys).
4. Run the application: `streamlit run app.py`

## Deliverables

- [x] Technical Documentation
- [ ] Working Prototype
- [ ] Damage Detection Model (via VLM)
- [ ] Cost Estimation Report
