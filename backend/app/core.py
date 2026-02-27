import json
import os
import re
from typing import Dict, Any, List
from .vision_model import VisionAgent

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

class ClaimEstimator:
    def __init__(self, parts_db_path: str = "data/parts_db.json", labor_rate: float = 500.0, provider: str = "mock", api_key: str = None):
        # labor_rate in INR (approx 500 INR/hr)
        
        # Determine path relative to this file
        base_path = os.path.dirname(os.path.abspath(__file__)) # app/
        backend_root = os.path.dirname(base_path) # backend/
        full_path = os.path.join(backend_root, parts_db_path)
        
        self.parts_db = self._load_parts_db(full_path)
        self.labor_rate = labor_rate
        self.vision_agent = VisionAgent(provider=provider, api_key=api_key)
        self.usd_to_inr = 85.0 # Approximate conversion rate

    def _load_parts_db(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Parts database not found at {path}")
            return {}

    def _search_part_price(self, part_name: str, car_info: str) -> tuple[float | None, str]:
        """
        Searches for the part price in India using DuckDuckGo.
        Returns (price, source_url) or (None, "") if not found.
        """
        if not DDGS:
            print("Web Search Disabled: DuckDuckGo library missing")
            return None, ""

        # Construct specific query for Indian market
        # Example: "Maruti Swift 2022 front bumper price India buy online"
        search_term = part_name.replace('_', ' ')
        if car_info and car_info != "Unknown Car":
            query = f"{car_info} {search_term} price in India buy online"
        else:
            query = f"{search_term} car part price India buy online"
             
        print(f"🔍 Web Search Query: '{query}'")
        
        try:
            # Get more results to increase chance of finding a price
            results = DDGS().text(query, max_results=5)
            
            for r in results:
                title = r.get('title', '')
                body = r.get('body', '')
                href = r.get('href', '')
                
                # Combine title and body for search
                text_content = f"{title} {body}"
                
                # Regex to find price in Rs. or ₹
                # Improved regex to handle: Rs. 1,200 | ₹ 1200 | INR 1200 | Rs 1500/-
                prices = re.findall(r'(?:Rs\.?|₹|INR)\s?([\d,]+)', text_content, re.IGNORECASE)
                
                if prices:
                    for p_str in prices:
                        try:
                            clean_price = float(p_str.replace(',', ''))
                            # Sanity check: Car parts usually > ₹100 and < ₹1,00,000 (except engines)
                            if 100 < clean_price < 100000:
                                print(f"✅ Found price for {part_name}: ₹{clean_price} (Source: {href})")
                                return clean_price, href
                        except ValueError:
                            continue
                            
        except Exception as e:
            print(f"❌ Web search failed: {e}")
            
        print(f"⚠️ No valid price found for {part_name} via web search.")
        return None, ""

    def _search_vehicle_info(self, registration_number: str) -> str | None:
        """
        Attempts to find vehicle make and model using the registration number via web search.
        Query example: "Vehicle details for KA01AB1234"
        """
        # Skip if no library or invalid registration number
        if not DDGS or not registration_number or "Unknown" in registration_number or "License" in registration_number:
            return None
            
        # Clean registration number (e.g., "KA-01-AB-1234" -> "KA01AB1234")
        reg_no = registration_number.replace("-", "").replace(" ", "").upper()
        
        # Basic validation for Indian plates (min 6 chars, e.g., KA01A1)
        if len(reg_no) < 6:
            return None

        # Query to find vehicle details associated with the plate
        query = f"vehicle details for {reg_no} India owner make model"
        print(f"🔍 Searching vehicle info for Registration: {reg_no}")
        
        try:
            # Get search results
            results = DDGS().text(query, max_results=5)
            
            # Common Indian car brands to check for in search snippets
            # This helps filter noise from search results
            brands = ["Maruti", "Suzuki", "Hyundai", "Tata", "Mahindra", "Toyota", "Honda", "Kia", "Volkswagen", "Skoda", "Renault", "Nissan", "Ford", "MG", "BMW", "Mercedes", "Audi"]
            
            for r in results:
                # Combine title and body for broader context
                text = (r.get('title', '') + " " + r.get('body', '')).lower()
                
                # Check if any car brand is mentioned in the search result for this plate
                for brand in brands:
                    if brand.lower() in text:
                        # If a brand is found, we assume it's likely the car's make
                        # To be more precise, we could look for model names near the brand
                        # For now, returning the Brand + "Vehicle" is better than "Unknown"
                        
                        # Try to find model names (simple heuristic)
                        # e.g. "Swift", "City", "Creta", "Nexon"
                        common_models = ["swift", "baleno", "creta", "seltos", "city", "amaze", "nexon", "harrier", "fortuner", "innova", "i20", "wagonr", "alto", "dzire"]
                        
                        found_model = ""
                        for model in common_models:
                            if model in text:
                                found_model = model.capitalize()
                                break
                        
                        detected_info = f"{brand} {found_model}".strip()
                        print(f"✅ Detected Vehicle from Web: {detected_info}")
                        return detected_info
                        
        except Exception as e:
            print(f"❌ Vehicle info search failed: {e}")
            
        return None

    def analyze_claim(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Full workflow: Image -> Vision AI -> Damage Assessment -> Cost Calculation -> Report
        """
        # Step 1: Analyze Image
        analysis_result = self.vision_agent.analyze_image(image_bytes)
        
        # Check for errors
        if "error" in analysis_result:
            return {
                "error": analysis_result["error"],
                "damage_assessment": {"damages": [], "car_info": "Unknown"},
                "cost_estimate": {"line_items": [], "summary": {"total_cost": 0}},
                "status": "Error"
            }

        # Step 1.5: Refine Car Info using Registration Number
        reg_no = analysis_result.get("registration_number")
        if reg_no:
            found_model = self._search_vehicle_info(reg_no)
            if found_model:
                print(f"✅ Refined Car Model: {found_model} (from Registration {reg_no})")
                analysis_result["car_info"] = found_model
                analysis_result["note"] = "Vehicle model refined using web search on registration number."

        # Step 2: Calculate Costs
        estimate = self._calculate_estimate(analysis_result)
        
        # Step 3: Combine Results
        report = {
            "damage_assessment": analysis_result,
            "cost_estimate": estimate,
            "status": "Pre-Approved" if estimate['summary']['total_cost'] < 50000 else "Needs Manual Review" 
        }
        
        return report

    def _calculate_estimate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        damages = analysis.get("damages", [])
        car_info = analysis.get("car_info", "Unknown Car")
        
        line_items = []
        total_parts_cost = 0.0
        total_labor_hours = 0.0
        
        for damage in damages:
            part_name = damage.get("part")
            severity = damage.get("severity", "moderate")
            description = damage.get("description", "")
            
            # Match with database for labor hours
            db_entry = self.parts_db.get(part_name)
            base_labor_hours = db_entry["labor_hours"] if db_entry else 1.0
            
            # 1. Try Web Search for Price
            part_cost, source_url = self._search_part_price(part_name, car_info)
            price_source = "Web Search" if part_cost else "Database Estimate"
            
            # 2. Fallback to DB Price (converted to INR)
            if part_cost is None:
                if db_entry:
                    part_cost = db_entry["part_cost"] * self.usd_to_inr
                else:
                    part_cost = 0.0
            
            # Calculate Labor
            severity_multiplier = 1.0
            if severity == "minor":
                severity_multiplier = 0.5
            elif severity == "severe":
                severity_multiplier = 1.5
                
            labor_hours = base_labor_hours * severity_multiplier
            labor_cost = labor_hours * self.labor_rate
            line_total = part_cost + labor_cost
            
            line_items.append({
                "part": part_name,
                "severity": severity,
                "description": description,
                "part_cost": part_cost,
                "labor_hours": labor_hours,
                "labor_cost": labor_cost,
                "total": line_total,
                "price_source": price_source,
                "source_url": source_url
            })
            
            total_parts_cost += part_cost
            total_labor_hours += labor_hours

        total_labor_cost = total_labor_hours * self.labor_rate
        subtotal = total_parts_cost + total_labor_cost
        tax = subtotal * 0.18  # 18% GST in India
        total_cost = subtotal + tax
        
        return {
            "line_items": line_items,
            "summary": {
                "total_parts_cost": total_parts_cost,
                "total_labor_hours": total_labor_hours,
                "labor_rate": self.labor_rate,
                "total_labor_cost": total_labor_cost,
                "subtotal": subtotal,
                "tax": tax,
                "total_cost": total_cost,
                "currency": "INR"
            }
        }
