import base64
import os
import json
import io
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
    from PIL import Image
except ImportError:
    Image = None

class VisionAgent:
    def __init__(self, provider="gemini", api_key=None):
        self.provider = provider
        self.api_key = api_key
        self.model_name = None

        # Handle custom model names for Ollama (e.g., "ollama:qwen3-vl:8b")
        if self.provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "gemini" and genai:
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.model_name = self._pick_gemini_model_name(self.model_name)
            self.client = genai.GenerativeModel(self.model_name)

    def _pick_gemini_model_name(self, preferred: str | None) -> str:
        env_model = os.getenv("GEMINI_MODEL")
        candidates = [m for m in [preferred, env_model, "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro-vision", "gemini-pro-vision"] if m]

        try:
            models = list(genai.list_models())
            supported = []
            for m in models:
                try:
                    methods = getattr(m, "supported_generation_methods", None) or []
                    if "generateContent" in methods:
                        supported.append(getattr(m, "name", ""))
                except Exception:
                    continue

            supported_set = set(supported)
            supported_short = set([s.split("models/", 1)[1] for s in supported if s.startswith("models/")])

            for c in candidates:
                if c in supported_short:
                    return c
                if c in supported_set:
                    return c
                if f"models/{c}" in supported_set:
                    return f"models/{c}"

            if supported:
                return supported[0]
        except Exception:
            pass

        return candidates[0]

    def analyze_image(self, images: Union[bytes, List[bytes]], mode: str = "full", detection_mode: str = "conservative") -> Dict[str, Any]:
        """
        Analyzes the car damage image(s) and returns a structured assessment.
        Accepts either a single bytes object or a list of bytes objects.
        """
        # Normalize input to list
        image_list = images if isinstance(images, list) else [images]
        if self.provider == "openai":
            return self._analyze_with_openai(image_list, mode, detection_mode)
        elif self.provider == "gemini":
            return self._analyze_with_gemini(image_list, mode, detection_mode)
        else:
            return {"error": f"Unsupported provider: {self.provider}", "damages": []}

    def _is_invalid_api_key_error(self, err: str) -> bool:
        s = (err or "").lower()
        phrases = [
            "invalid api key",
            "api key not valid",
            "api-key not valid",
            "incorrect api key",
            "incorrect api-key",
            "authentication",
            "unauthorized",
            "permission denied",
            "permission_denied",
            "401",
            "403",
        ]
        return any(p in s for p in phrases)

    def _invalid_key_payload(self, provider_label: str) -> Dict[str, Any]:
        return {
            "error": f"Invalid {provider_label} API key. Please paste a valid key and try again.",
            "error_type": "invalid_api_key",
            "damages": [],
        }



    def _analyze_with_openai(self, image_list: List[bytes], mode: str, detection_mode: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "OpenAI client not initialized"}

        try:
            strict = "Only report damage if clearly visible; if unsure, do NOT include it." if detection_mode == "conservative" else "Be thorough in finding damage across images."
            if mode == "damages_only":
                user_text = f"Identify all damaged parts across all images. {strict}"
            else:
                user_text = f"Identify vehicle details if possible and list damaged parts across images. {strict}"
            content_list = [{"type": "text", "text": user_text}]
            
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
                        "content": """You are an expert car insurance adjuster.
                        Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
                        Return ONLY valid JSON. Format:
                        {"car_info":"Make Model Year (or Unknown)","registration_number":"License Plate (or Unknown)","damages":[{"part":"part_key","severity":"minor|moderate|severe","description":"detailed description"}]}"""
                    },
                    {
                        "role": "user",
                        "content": content_list
                    }
                ],
                max_tokens=600 if mode == "damages_only" else 1000,
                temperature=0.2 if detection_mode == "conservative" else 0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            err = str(e)
            if self._is_invalid_api_key_error(err):
                return self._invalid_key_payload("OpenAI")
            return {"error": err, "damages": []}

    def _analyze_with_gemini(self, image_list: List[bytes], mode: str, detection_mode: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Gemini client not initialized"}

        try:
            # Prepare content for Gemini
            # Gemini accepts list of [prompt, image1, image2, ...]
            
            strict = "Only report damage if clearly visible; if unsure, return an empty damages list." if detection_mode == "conservative" else "Be thorough in detecting damage."
            if mode == "damages_only":
                prompt = """
                Identify all damaged parts across all images. Return ONLY valid JSON.
                Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
                {"car_info":"Unknown","registration_number":"Unknown","damages":[{"part":"part_key","severity":"minor|moderate|severe","description":"detailed description"}]}
                """
            else:
                prompt = """
                Identify the car Make/Model/Year if possible, the license plate if visible, and all damaged parts.
                Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.
                Return ONLY valid JSON.
                {"car_info":"Make Model Year (or Unknown)","registration_number":"License Plate (or Unknown)","damages":[{"part":"part_key","severity":"minor|moderate|severe","description":"detailed description"}]}
                """

            prompt = f"{prompt}\n\n{strict}" 
            
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
            err = str(e)
            if self.provider == "gemini" and ("models/" in err and "not found" in err.lower()):
                try:
                    self.model_name = self._pick_gemini_model_name(None)
                    self.client = genai.GenerativeModel(self.model_name)
                    response = self.client.generate_content(content)
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[3:]
                    if text.endswith("```"):
                        text = text[:-3]
                    return json.loads(text.strip())
                except Exception:
                    pass

            if self.provider == "gemini" and "not found" in err.lower():
                return {
                    "error": "Gemini model not available for this API key. Use a Google AI Studio Gemini API key and set a supported model (e.g. gemini-1.5-pro).",
                    "damages": []
                }

            if self._is_invalid_api_key_error(err):
                return self._invalid_key_payload("Gemini")

            return {"error": err, "damages": []}

    def _analyze_with_ollama(self, image_list: List[bytes], mode: str, detection_mode: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Ollama client not initialized"}
            
        try:
            # Note: Ollama python client currently processes one image at a time or depends on the model's capabilities
            # For simplicity, we'll analyze the first image (Front view usually) or merge results in future
            # Here we will try to send the first image as a sample
            
            # LLaVA expects 'images' as a list of paths or bytes
            # We will use the first image for now as LLaVA context window is limited
            
            strict = "Only report damage if clearly visible; if unsure, return an empty damages list." if detection_mode == "conservative" else "Be thorough in detecting damage."
            if mode == "damages_only":
                prompt = """
                You are an expert car insurance adjuster.
                Identify all damaged parts across all images.

                IMPORTANT:
                - Look VERY closely for damage. If the car is crushed / major impact, mark relevant parts as "severe".
                - Only return empty damages if the car is clearly undamaged.

                Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.

                Return ONLY valid JSON:
                {"car_info":"Unknown","registration_number":"Unknown","damages":[{"part":"part_key","severity":"minor|moderate|severe","description":"detailed description"}]}
                """
            else:
                prompt = """
                You are an expert car insurance adjuster.
                Read the license plate if visible in any image and identify all damaged parts.

                IMPORTANT:
                - You MUST try to read the license plate from ANY image (front or rear). If not readable set "registration_number" to "Unknown".
                - Look VERY closely for damage. If the car is crushed / major impact, mark relevant parts as "severe".

                Supported parts keys: bumper_front, bumper_rear, fender_left, fender_right, door_front_left, door_front_right, door_rear_left, door_rear_right, hood, trunk_lid, headlight_left, headlight_right, taillight_left, taillight_right, windshield, side_mirror_left, side_mirror_right.

                Return ONLY valid JSON:
                {"car_info":"Make Model Year (or Unknown)","registration_number":"License Plate (or Unknown)","damages":[{"part":"part_key","severity":"minor|moderate|severe","description":"detailed description"}]}
                """

            prompt = f"{prompt}\n\n{strict}" 
            
            # Convert bytes to base64 for Ollama
            # Ollama Python library handles bytes directly for 'images'
            
            response = self.client.chat(
                model=self.model_name,
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
            content = content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
            
        except Exception as e:
            err = str(e)
            if self._is_invalid_api_key_error(err):
                return self._invalid_key_payload("Ollama")
            return {"error": f"Ollama Error: {err}", "damages": []}
