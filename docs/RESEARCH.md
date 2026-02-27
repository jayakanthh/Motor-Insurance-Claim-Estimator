# Research Notes - Motor Insurance Claim Estimator

## Goals
- Produce a reliable estimate from 4 mandatory vehicle angles (+ optional close-ups).
- Extract registration number to fetch vehicle make/model/year for better part pricing queries.
- Reduce false positives (hallucinated damages) while still catching real damage.
- Keep runtime low enough for a smooth UX.

## Observations From Current Prototype
- Vision models can hallucinate “generic damages” (e.g., “Damage to the front bumper”) on clean vehicles.
- Local multimodal models can have constraints (some don’t support multiple images in one request).
- Web price lookup is a major latency source and can dominate total runtime.
- Plate OCR can be slow and unreliable depending on angle/lighting/blur.

## AI Model Strategy (Provider + Model)
### Cloud models (highest quality)
- **OpenAI (GPT-4o)**: strong overall for multi-image understanding and structured outputs.
- **Gemini 1.5**: strong multimodal; output formatting can require cleaning.

### Local models (lowest cost, runs offline)
- **Ollama (llava:13b)**: good general visual reasoning; tends to be more stable on “overall scene” than smaller models.
- **Ollama (minicpm-v)**: fast and can be good at text/plate-like cues; may under/over-call damage depending on prompt.

### Compatibility note (multi-image)
- Some local models/APIs perform best with a single image input.
- To preserve the “multi-angle” signal, a practical workaround is a **2x2 collage** of the 4 required views.

## False Positive Reduction (Damage Hallucinations)
### Root causes
- Prompts that encourage “always find damage” produce hallucinations.
- Models may output plausible-sounding damage descriptions without visual evidence.

### Mitigations
- **Conservative prompting**: explicitly require “only report damage if clearly visible; if unsure, return empty damages”.
- **Post-filtering**: drop damages with generic/no-evidence descriptions (e.g., “Damage to …”) unless they include evidence keywords.
- **User control**: expose a toggle:
  - Conservative (fewer false positives)
  - Sensitive (find more damage, tolerate more false positives)

### Recommended evaluation
- Build a small labeled dataset:
  - 20 clean cars (different lighting/backgrounds)
  - 20 minor damage cases
  - 20 severe damage cases
- Track:
  - False positive rate on clean cars
  - Miss rate on minor/severe damage
  - Average runtime

## Registration Number Flow
### Why it matters
- Make/model/year improves part query precision and pricing quality.

### Practical approach
- Treat registration number as **required**, but allow two ways:
  1. **AI reads plate** from front/rear
  2. **Manual input** if the plate is not readable

### Performance optimization
- If manual registration number is provided, skip plate OCR and run **damages-only** mode to reduce runtime.

## Part Pricing Strategy
### Sources
- **Web search** (e.g., reputable marketplaces/parts sites) for live-ish pricing.
- **Local DB fallback** for baseline estimates.
- **Average estimate fallback** when neither web nor DB has the part.

### Latency and reliability
- Web search can be slow and sometimes fails.
- Recommended controls:
  - Cap web lookups per estimate (e.g., top 6 damages by severity).
  - Run lookups in parallel with a small worker pool.
  - Cache repeated lookups within a request.

## Performance Hotspots
- Vision inference (cloud latency or local inference time)
- Web price lookup
- Large image payloads

### Speed levers
- Resize images before inference (token/compute reduction)
- Skip plate OCR when manual reg is provided
- Parallelize and cap price lookups

## PDF Export
### Approach
- Generate PDFs on the backend using a deterministic renderer (e.g., `reportlab`).
- Export should include:
  - Vehicle details
  - Damage list
  - Cost summary
  - Line items

## Recommended Next Research Steps
- Add a “Fast mode” that disables web lookup (DB/avg only) for near-instant estimates.
- Add a second-pass verification step for damages:
  - Ask model to justify each damage with visible evidence.
  - Drop items without evidence.
- Improve plate extraction accuracy with a dedicated OCR step (optional) for front/rear crops.

