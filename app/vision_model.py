import base64
import os
import json
import random
import time
from typing import List, Dict, Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

class VisionAgent:
    def __init__(self, provider="mock", api_key=None):
        self.provider = provider
        self.api_key = api_key
        
        if self.provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "gemini":
            # self.client = genai.GenerativeModel('gemini-1.5-pro')
            pass

    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyzes the car damage image and returns a structured assessment.
        """
        # Preprocess using OpenCV if available
        if cv2 and np:
            try:
                image_bytes = self._preprocess_image(image_bytes)
            except Exception as e:
                print(f"Warning: Image preprocessing failed: {e}")

        if self.provider == "openai":
            return self._analyze_with_openai(image_bytes)
        elif self.provider == "gemini":
            return self._analyze_with_gemini(image_bytes)
        else:
            return self._mock_analysis(image_bytes)

    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Resizes and enhances image using OpenCV.
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_bytes

        # Resize if too large (max 1024px) to save tokens and bandwidth
        height, width = img.shape[:2]
        max_dim = 1024
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This helps highlight scratches and dents
        try:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl,a,b))
            img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        except Exception:
            pass # Skip if enhancement fails

        # Encode back to bytes
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()

    def _mock_analysis(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Simulates AI analysis for demo purposes.
        """
        time.sleep(2)  # Simulate processing time
        
        # Mock damage scenarios
        scenarios = [
            {
                "damages": [
                    {"part": "bumper_front", "severity": "moderate", "description": "Dent and scratch on the left side"},
                    {"part": "headlight_left", "severity": "severe", "description": "Cracked lens"}
                ],
                "confidence": 0.95
            },
            {
                "damages": [
                    {"part": "door_front_right", "severity": "minor", "description": "Deep scratch"},
                    {"part": "side_mirror_right", "severity": "moderate", "description": "Broken housing"}
                ],
                "confidence": 0.88
            },
            {
                "damages": [
                    {"part": "bumper_rear", "severity": "severe", "description": "Major impact damage, detached"},
                    {"part": "taillight_left", "severity": "moderate", "description": "Cracked"}
                ],
                "confidence": 0.92
            }
        ]
        
        return random.choice(scenarios)

    def _analyze_with_openai(self, image_bytes: bytes) -> Dict[str, Any]:
        if not self.client:
            return {"error": "OpenAI client not initialized"}

        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert car insurance adjuster. Analyze the image and identify damaged parts.
                        Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
                        Return ONLY valid JSON. Format: {"damages": [{"part": "part_key", "severity": "minor|moderate|severe", "description": "brief description"}]}"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this car damage."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "damages": []}

    def _analyze_with_gemini(self, image_bytes: bytes) -> Dict[str, Any]:
        # Placeholder for Gemini implementation
        return self._mock_analysis(image_bytes)
