# System Architecture

## Overview

The Motor Claim Estimator is designed as a modular application with a clear separation between the User Interface, Business Logic, and AI Integration.

## High-Level Diagram

```
+----------------+       +-------------------+       +---------------------+
|   User (Web)   | ----> |   Streamlit UI    | ----> |   ClaimEstimator    |
+----------------+       | (frontend/ui.py)  |       |   (app/core.py)     |
                         +-------------------+       +----------+----------+
                                                                |
                                                                v
                                                     +---------------------+
                                                     |     VisionAgent     |
                                                     | (app/vision_model.py)|
                                                     +----------+----------+
                                                                |
                                                 +--------------+--------------+
                                                 |                             |
                                         +-------v-------+             +-------v-------+
                                         |  OpenAI API   |             |  Mock Engine  |
                                         |   (GPT-4o)    |             |   (Random)    |
                                         +---------------+             +---------------+
```

## Component Details

### 1. Frontend (`frontend/ui.py`)
- **Framework**: Streamlit
- **Responsibilities**:
  - Handle user image uploads.
  - Display configuration options (API keys, Model selection).
  - Visualize damage assessment (bounding boxes or text descriptions).
  - Present cost estimation tables and summaries.

### 2. Core Logic (`app/core.py`)
- **Class**: `ClaimEstimator`
- **Responsibilities**:
  - Orchestrate the workflow (Image -> Analysis -> Cost).
  - Load and query the Parts Database (`data/parts_db.json`).
  - Calculate labor costs based on severity and hourly rates.
  - Apply business rules (e.g., Pre-approval threshold).

### 3. Vision Model (`app/vision_model.py`)
- **Class**: `VisionAgent`
- **Responsibilities**:
  - Abstract the AI provider (OpenAI, Gemini, Mock).
  - Prepare image data (Base64 encoding).
  - Construct prompts for the Vision LLM.
  - Parse JSON responses from the LLM.

### 4. Data Layer (`data/`)
- **Parts Database**: JSON file mapping part names to base costs and labor hours.
- **Future Extension**: Could be replaced by a SQL database or external API.

## Data Flow

1. **Upload**: User uploads an image via Streamlit.
2. **Analysis**: `VisionAgent` sends the image to the selected LLM with a prompt to identify damaged parts and severity.
3. **Parsing**: The LLM returns a JSON structure listing damaged parts.
4. **Estimation**: `ClaimEstimator` iterates through the damaged parts:
   - Look up part cost in `parts_db.json`.
   - Calculate labor hours (Base Hours * Severity Multiplier).
   - Compute total cost (Part + Labor + Tax).
5. **Report**: The final structured report is sent back to the UI for display.

## Deployment
- Can be deployed on Streamlit Cloud, Docker, or any Python-supported environment.
