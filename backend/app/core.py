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

    def _search_part_price(self, part_name: str, car_info: str) -> float:
        """
        Searches for the part price in India using DuckDuckGo.
        Returns the price in INR if found, otherwise None.
        """
        if not DDGS:
            return None

        query = f"price of {part_name} for {car_info} in India in rupees"
        if car_info == "Unknown Car":
             query = f"price of {part_name} car part in India in rupees"
             
        print(f"Searching web for: {query}")
        
        try:
            results = DDGS().text(query, max_results=3)
            for r in results:
                body = r.get('body', '')
                # Regex to find price in Rs. or ₹
                # Matches: Rs. 1,200 or ₹ 1200 or INR 1200
                prices = re.findall(r'(?:Rs\.?|₹|INR)\s?([\d,]+)', body, re.IGNORECASE)
                if prices:
                    # Clean and convert first found price
                    try:
                        price_str = prices[0].replace(',', '')
                        price = float(price_str)
                        if price > 100: # Filter out unrealistic small numbers
                            print(f"Found price for {part_name}: ₹{price}")
                            return price
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Web search failed: {e}")
            
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
            part_cost = self._search_part_price(part_name.replace('_', ' '), car_info)
            
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
                "total": line_total
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
