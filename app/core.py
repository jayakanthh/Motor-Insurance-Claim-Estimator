import json
import os
from typing import Dict, Any, List
from .vision_model import VisionAgent

class ClaimEstimator:
    def __init__(self, parts_db_path: str = "data/parts_db.json", labor_rate: float = 75.0):
        # Determine path relative to this file
        base_path = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_path)
        full_path = os.path.join(project_root, parts_db_path)
        
        self.parts_db = self._load_parts_db(full_path)
        self.labor_rate = labor_rate
        self.vision_agent = VisionAgent()

    def _load_parts_db(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Parts database not found at {path}")
            return {}

    def analyze_claim(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Full workflow: Image -> Vision AI -> Damage Assessment -> Cost Calculation -> Report
        """
        # Step 1: Analyze Image
        analysis_result = self.vision_agent.analyze_image(image_bytes)
        
        # Step 2: Calculate Costs
        estimate = self._calculate_estimate(analysis_result)
        
        # Step 3: Combine Results
        report = {
            "damage_assessment": analysis_result,
            "cost_estimate": estimate,
            "status": "Pre-Approved" if estimate['summary']['total_cost'] < 2000 else "Needs Manual Review" 
        }
        
        return report

    def _calculate_estimate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        damages = analysis.get("damages", [])
        
        line_items = []
        total_parts_cost = 0.0
        total_labor_hours = 0.0
        
        for damage in damages:
            part_name = damage.get("part")
            severity = damage.get("severity", "moderate")
            
            # Match with database
            db_entry = self.parts_db.get(part_name)
            
            if db_entry:
                part_cost = db_entry["part_cost"]
                base_labor_hours = db_entry["labor_hours"]
                
                # Simple severity multiplier for labor
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
                    "description": damage.get("description", ""),
                    "part_cost": part_cost,
                    "labor_hours": labor_hours,
                    "labor_cost": labor_cost,
                    "total": line_total
                })
                
                total_parts_cost += part_cost
                total_labor_hours += labor_hours
            else:
                # Part not in DB
                line_items.append({
                    "part": part_name,
                    "severity": severity,
                    "description": "Part not found in database, manual estimation required",
                    "part_cost": 0.0,
                    "labor_hours": 0.0,
                    "labor_cost": 0.0,
                    "total": 0.0
                })

        total_labor_cost = total_labor_hours * self.labor_rate
        subtotal = total_parts_cost + total_labor_cost
        tax = subtotal * 0.10  # 10% tax
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
                "total_cost": total_cost
            }
        }
