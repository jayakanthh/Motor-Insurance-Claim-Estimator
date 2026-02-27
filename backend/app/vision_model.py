import base64
import os
import json
import random
import time
from typing import List, Dict, Any, Union

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import ollama
except ImportError:
    ollama = None

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
        elif self.provider == "gemini" and genai:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
        elif self.provider == "ollama" and ollama:
            self.client = ollama

    def analyze_image(self, images: Union[bytes, List[bytes]]) -> Dict[str, Any]:
        """
        Analyzes the car damage image(s) and returns a structured assessment.
        Accepts either a single bytes object or a list of bytes objects.
        """
        # Normalize input to list
        if isinstance(images, bytes):
            image_list = [images]
        else:
            image_list = images

        # Preprocess using OpenCV if available
        if cv2 and np:
            processed_images = []
            for img_bytes in image_list:
                try:
                    processed_images.append(self._preprocess_image(img_bytes))
                except Exception as e:
                    print(f"Warning: Image preprocessing failed: {e}")
                    processed_images.append(img_bytes)
            image_list = processed_images

        if self.provider == "openai":
            return self._analyze_with_openai(image_list)
        elif self.provider == "gemini":
            return self._analyze_with_gemini(image_list)
        elif self.provider == "ollama":
            return self._analyze_with_ollama(image_list)
        else:
            return self._mock_analysis(image_list)

    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        Resizes and enhances image using OpenCV.
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_bytes

        # Resize if too large (max 2048px) to save tokens and bandwidth
        height, width = img.shape[:2]
        max_dim = 2048
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

    def _mock_analysis(self, image_list: List[bytes]) -> Dict[str, Any]:
        """
        Simulates AI analysis for demo purposes.
        """
        time.sleep(2)  # Simulate processing time
        
        # Mock damage scenarios
        scenarios = [
            {
                "car_info": "Toyota Camry 2020",
                "registration_number": "KA-01-AB-1234",
                "damages": [
                    {"part": "bumper_front", "severity": "moderate", "description": "Dent and scratch on the left side"},
                    {"part": "headlight_left", "severity": "severe", "description": "Cracked lens"}
                ],
                "confidence": 0.95
            },
            {
                "car_info": "Honda Civic 2019",
                "registration_number": "MH-02-XY-9876",
                "damages": [
                    {"part": "door_front_right", "severity": "minor", "description": "Deep scratch"},
                    {"part": "side_mirror_right", "severity": "moderate", "description": "Broken housing"}
                ],
                "confidence": 0.88
            },
            {
                "car_info": "Hyundai Creta 2021",
                "registration_number": "DL-10-CD-5678",
                "damages": [
                    {"part": "bumper_rear", "severity": "severe", "description": "Major impact damage, detached"},
                    {"part": "taillight_left", "severity": "moderate", "description": "Cracked"}
                ],
                "confidence": 0.92
            },
            {
                "car_info": "Maruti Suzuki Swift 2023",
                "registration_number": "TS-09-EF-4321",
                "damages": [],
                "confidence": 0.98
            }
        ]
        
        return random.choice(scenarios)

    def _analyze_with_openai(self, image_list: List[bytes]) -> Dict[str, Any]:
        if not self.client:
            return {"error": "OpenAI client not initialized"}

        try:
            content_list = [{"type": "text", "text": "Analyze these car damage photos. Identify all damaged parts across all images."}]
            
            for img_bytes in image_list:
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                content_list.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert car insurance adjuster. Analyze the provided images and identify damaged parts.
                        1. Identify the car Make, Model and Year if possible.
                        2. Identify the Registration Number (License Plate) if visible.
                        3. Identify all damaged parts.
                        
                        If there are NO DAMAGES and the car is in good condition, return an empty "damages" list.

                        Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
                        Return ONLY valid JSON. Format: 
                        {
                            "car_info": "Make Model Year (or Unknown)",
                            "registration_number": "License Plate (or Unknown)",
                            "damages": [{"part": "part_key", "severity": "minor|moderate|severe", "description": "brief description"}]
                        }"""
                    },
                    {
                        "role": "user",
                        "content": content_list
                    }
                ],
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "damages": []}

    def _analyze_with_gemini(self, image_list: List[bytes]) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Gemini client not initialized"}

        try:
            # Prepare content for Gemini
            # Gemini accepts list of [prompt, image1, image2, ...]
            
            prompt = """
            You are an expert car insurance adjuster. Analyze these car damage photos.
            1. Identify the car Make, Model and Year if possible (e.g. "Toyota Camry 2022"). If unknown, say "Unknown Car".
            2. Identify the Registration Number (License Plate) if visible.
            3. Identify all damaged parts across all images.
            
            If there are NO DAMAGES and the car is in good condition, return an empty "damages" list.
            
            Supported parts keys: 
            bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
            
            Return ONLY valid JSON. Format: 
            {
                "car_info": "Make Model Year (or Unknown)",
                "registration_number": "License Plate (or Unknown)",
                "damages": [{"part": "part_key", "severity": "minor|moderate|severe", "description": "brief description"}]
            }
            """
            
            content = [prompt]
            
            for img_bytes in image_list:
                # Convert bytes to dictionary expected by Gemini SDK or use PIL/Blob
                # Gemini Python SDK supports passing dictionary with mime_type and data
                content.append({
                    "mime_type": "image/jpeg",
                    "data": img_bytes
                })

            response = self.client.generate_content(content)
            
            # Clean response text (sometimes Gemini adds markdown block quotes)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text.strip())
            
        except Exception as e:
            return {"error": str(e), "damages": []}

    def _analyze_with_ollama(self, image_list: List[bytes]) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Ollama client not initialized"}
            
        try:
            # Note: Ollama python client currently processes one image at a time or depends on the model's capabilities
            # For simplicity, we'll analyze the first image (Front view usually) or merge results in future
            # Here we will try to send the first image as a sample
            
            # LLaVA expects 'images' as a list of paths or bytes
            # We will use the first image for now as LLaVA context window is limited
            
            prompt = """
            Analyze these car damage images to extract vehicle details and damage information for cost estimation.
            
            1. IDENTIFY VEHICLE:
               - Make, Model, Year (e.g., "Maruti Swift 2022")
               - Registration Number / License Plate (Check all images carefully)
            
            2. DETECT DAMAGES:
               - List EVERY damaged part.
               - Assess severity (minor, moderate, severe).
               - Provide a detailed description.
            
            If there are NO DAMAGES and the car is in good condition, return an empty "damages" list.
            
            Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
            
            Return ONLY valid JSON. Format: 
            {
                "car_info": "Make Model Year (or Unknown)",
                "registration_number": "License Plate (or Unknown)",
                "damages": [{"part": "part_key", "severity": "minor|moderate|severe", "description": "detailed description"}]
            }
            """
            
            # Convert bytes to base64 for Ollama
            # Ollama Python library handles bytes directly for 'images'
            
            response = self.client.chat(
                model='minicpm-v',
                messages=[
                  {
                    'role': 'user',
                    'content': prompt,
                    'images': image_list # Send ALL images
                  }
                ],
                format='json'
            )
            
            content = response['message']['content']
            
            # Clean content for JSON parsing
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Ollama Error: {str(e)}", "damages": []}
