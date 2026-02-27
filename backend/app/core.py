import json
import os
import re
import concurrent.futures
from typing import Dict, Any
from .vision_model import VisionAgent
from .rto_lookup import RTOLookup

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
        self.rto_lookup = RTOLookup()
        self.usd_to_inr = 85.0 # Approximate conversion rate
        self.avg_part_cost_inr = self._compute_average_part_cost_inr()
        self.price_cache: Dict[str, tuple[float | None, str]] = {}

    def _compute_average_part_cost_inr(self) -> float:
        costs = []
        for v in (self.parts_db or {}).values():
            try:
                costs.append(float(v.get("part_cost")))
            except Exception:
                continue
        if not costs:
            return 3000.0
        return (sum(costs) / len(costs)) * self.usd_to_inr

    def _normalize_registration_number(self, registration_number: str | None) -> str | None:
        if not registration_number:
            return None
        reg = registration_number.replace("-", "").replace(" ", "").upper().strip()
        if len(reg) < 6:
            return None
        if not reg.isalnum():
            return None
        return reg

    def _load_parts_db(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Parts database not found at {path}")
            return {}

    def _search_part_price(self, part_name: str, car_info: str) -> tuple[float | None, str]:
        """
        Searches for the part price in India using DuckDuckGo, targeting reputable auto parts sites.
        Returns (price, source_url) or (None, "") if not found.
        """
        if not DDGS:
            print("Web Search Disabled: DuckDuckGo library missing")
            return None, ""

        cache_key = f"{car_info}|{part_name}".lower()
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]

        search_term = part_name.replace('_', ' ')
        
        # 1. First attempt: Site-specific searches for high accuracy
        # We'll try the most reliable one first: boodmo.com (very popular in India)
        
        sites_to_try = ["boodmo.com", "amazon.in"]
        
        for site in sites_to_try:
            if car_info and car_info != "Unknown Car":
                query = f"site:{site} {car_info} {search_term} price"
            else:
                query = f"site:{site} {search_term} price car part"
                
            print(f"🔍 Reputable Site Search ({site}): '{query}'")
            
            try:
                results = DDGS().text(query, max_results=3)
                price, url = self._extract_price_from_results(results, part_name)
                if price:
                    self.price_cache[cache_key] = (price, url)
                    return price, url
            except Exception as e:
                print(f"⚠️ Search failed for {site}: {e}")

        # 2. Second attempt: General search with "buy online India"
        if car_info and car_info != "Unknown Car":
            query = f"{car_info} {search_term} price in India buy online"
        else:
            query = f"{search_term} car part price India buy online"
             
        print(f"🔍 General Web Search: '{query}'")
        
        try:
            results = DDGS().text(query, max_results=5)
            price, url = self._extract_price_from_results(results, part_name)
            if price:
                self.price_cache[cache_key] = (price, url)
                return price, url
                            
        except Exception as e:
            print(f"❌ General web search failed: {e}")
            
        print(f"⚠️ No valid price found for {part_name} via web search.")
        self.price_cache[cache_key] = (None, "")
        return None, ""

    def _extract_price_from_results(self, results, part_name):
        """Helper to extract price from search results"""
        for r in results:
            title = r.get('title', '')
            body = r.get('body', '')
            href = r.get('href', '')
            
            # Combine title and body for search
            text_content = f"{title} {body}"
            
            # Regex to find price in Rs. or ₹
            # Handles: Rs. 1,200 | ₹ 1200 | INR 1200 | ₹1,200.00
            prices = re.findall(r'(?:Rs\.?|₹|INR)\s?([\d,]+(?:\.\d{2})?)', text_content, re.IGNORECASE)
            
            if prices:
                for p_str in prices:
                    try:
                        clean_price = float(p_str.replace(',', ''))
                        # Sanity check: Car parts usually > ₹100 and < ₹1,50,000
                        if 100 < clean_price < 150000:
                            print(f"✅ Found price for {part_name}: ₹{clean_price} (Source: {href})")
                            return clean_price, href
                    except ValueError:
                        continue
        return None, ""

    def _search_vehicle_info(self, registration_number: str) -> str | None:
        """
        Attempts to find vehicle make and model using the registration number.
        Uses RTOLookup module which leverages web search/scraping.
        """
        if not registration_number or "Unknown" in registration_number or "License" in registration_number:
            return None
            
        return self.rto_lookup.get_vehicle_details(registration_number)

    def _analyze_claim(self, image_bytes: bytes, registration_number: str | None = None, detection_mode: str = "conservative") -> Dict[str, Any]:
        """
        Full workflow: Image -> Vision AI -> Damage Assessment -> Cost Calculation -> Report
        """
        manual_reg = self._normalize_registration_number(registration_number)
        mode = "damages_only" if manual_reg else "full"

        analysis_result = self.vision_agent.analyze_image(image_bytes, mode=mode, detection_mode=detection_mode)
        
        # Check for errors
        if "error" in analysis_result:
            return {
                "error": analysis_result["error"],
                "damage_assessment": {"damages": [], "car_info": "Unknown"},
                "cost_estimate": {"line_items": [], "summary": {"total_cost": 0}},
                "status": "Error"
            }

        if manual_reg:
            analysis_result["registration_number"] = manual_reg

        reg_no = self._normalize_registration_number(analysis_result.get("registration_number"))
        if not reg_no:
            return {
                "error": "Registration number is required. Provide a clear number plate photo or enter it manually.",
                "damage_assessment": {"damages": [], "car_info": "Unknown", "registration_number": "Unknown"},
                "cost_estimate": {"line_items": [], "summary": {"total_cost": 0}},
                "status": "Error"
            }

        analysis_result["registration_number"] = reg_no
        found_model = self._search_vehicle_info(reg_no)
        if found_model:
            analysis_result["car_info"] = found_model
            analysis_result["note"] = "Vehicle model refined using registration number lookup."

        if detection_mode == "conservative":
            analysis_result["damages"] = self._filter_damages_for_evidence(analysis_result.get("damages", []))

        # Step 2: Calculate Costs
        estimate = self._calculate_estimate(analysis_result)
        
        # Step 3: Combine Results
        report = {
            "damage_assessment": analysis_result,
            "cost_estimate": estimate,
            "status": "Estimated"
        }
        
        return report

    def analyze_claim(self, image_bytes: bytes, registration_number: str | None = None, detection_mode: str = "conservative") -> Dict[str, Any]:
        return self._analyze_claim(image_bytes, registration_number=registration_number, detection_mode=detection_mode)

    def _filter_damages_for_evidence(self, damages: list[dict]) -> list[dict]:
        evidence_words = {
            "dent",
            "scratch",
            "crack",
            "broken",
            "missing",
            "misalign",
            "deform",
            "scuff",
            "tear",
            "crease",
            "bent",
            "shatter",
            "paint",
            "chip",
        }
        filtered = []
        for d in damages or []:
            desc = str(d.get("description", "") or "").lower()
            if not desc:
                continue
            if any(w in desc for w in evidence_words):
                filtered.append(d)
        return filtered

    def _calculate_estimate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        damages = analysis.get("damages", [])
        car_info = analysis.get("car_info", "Unknown Car")

        def severity_rank(s: str) -> int:
            if s == "severe":
                return 3
            if s == "moderate":
                return 2
            if s == "minor":
                return 1
            return 0

        damages_sorted = sorted(damages, key=lambda d: severity_rank(d.get("severity", "moderate")), reverse=True)
        max_web_lookups = 6
        web_targets = [d.get("part") for d in damages_sorted[:max_web_lookups] if d.get("part")]

        web_results: Dict[str, tuple[float | None, str]] = {}
        if web_targets:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(web_targets))) as ex:
                future_map = {
                    ex.submit(self._search_part_price, part, car_info): part
                    for part in web_targets
                }
                for fut in concurrent.futures.as_completed(future_map):
                    part = future_map[fut]
                    try:
                        web_results[part] = fut.result()
                    except Exception:
                        web_results[part] = (None, "")
        
        line_items = []
        total_parts_cost = 0.0
        total_labor_hours = 0.0
        
        for damage in damages_sorted:
            part_name = damage.get("part")
            severity = damage.get("severity", "moderate")
            description = damage.get("description", "")
            
            # Match with database for labor hours
            db_entry = self.parts_db.get(part_name)
            base_labor_hours = db_entry["labor_hours"] if db_entry else 1.0
            
            part_cost = None
            source_url = ""
            price_source = "Database Estimate"

            if part_name in web_results:
                part_cost, source_url = web_results[part_name]
                if part_cost is not None:
                    price_source = "Web Search"
            
            # 2. Fallback to DB Price (converted to INR) or average estimate
            if part_cost is None:
                if db_entry:
                    part_cost = db_entry["part_cost"] * self.usd_to_inr
                    price_source = "Database Estimate"
                else:
                    part_cost = self.avg_part_cost_inr
                    price_source = "Average Estimate"
                    source_url = ""
            
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
