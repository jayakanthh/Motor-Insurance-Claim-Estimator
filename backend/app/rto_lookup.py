import requests
from bs4 import BeautifulSoup
import re
import time

class RTOLookup:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }

    def get_vehicle_details(self, registration_number: str) -> str | None:
        if not registration_number or len(registration_number) < 6:
            return None
            
        reg_no = registration_number.replace("-", "").replace(" ", "").upper()
        print(f"🔍 RTO Lookup initiated for: {reg_no}")

        # Strategy 1: Direct DuckDuckGo Search for "CarInfo" page
        # Since scraping carinfo.app directly often hits captchas/Cloudflare,
        # we search for the specific carinfo page indexed by search engines.
        try:
            from duckduckgo_search import DDGS
            query = f"site:carinfo.app {reg_no} vehicle details"
            results = DDGS().text(query, max_results=3)
            
            for r in results:
                title = (r.get('title', '') or '').strip()
                body = (r.get('body', '') or '').strip()

                segment = ""
                if " - " in title:
                    parts = [p.strip() for p in title.split(" - ") if p.strip()]
                    if len(parts) >= 2:
                        segment = parts[1]
                if not segment:
                    segment = title

                combined = f"{segment} {body}".strip()
                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", combined)
                year = year_match.group(0) if year_match else ""

                words = re.split(r"\s+", segment)
                words = [w for w in words if w and w.lower() not in {"owner", "details", "vehicle", "rto", "registration"}]
                if words:
                    make_model = " ".join(words[:3]).strip()
                    result = f"{make_model} {year}".strip()
                    if len(result) > 3:
                        return result
                            
        except Exception as e:
            print(f"⚠️ Strategy 1 (DDG) failed: {e}")

        # Strategy 2: Fallback to general search (already implemented in core.py, but moving logic here)
        return self._heuristic_search(reg_no)

    def _heuristic_search(self, reg_no: str) -> str | None:
        try:
            from duckduckgo_search import DDGS
            query = f"vehicle details for {reg_no} India owner make model"
            results = DDGS().text(query, max_results=5)
            
            brands = ["Maruti", "Suzuki", "Hyundai", "Tata", "Mahindra", "Toyota", "Honda", "Kia", "Volkswagen", "Skoda", "Renault", "Nissan", "Ford", "MG"]
            
            for r in results:
                text = (r.get('title', '') + " " + r.get('body', '')).lower()
                for brand in brands:
                    if brand.lower() in text:
                        # Heuristic extraction
                        words = text.split()
                        try:
                            idx = words.index(brand.lower())
                            make = words[idx].capitalize()
                            model = words[idx+1].capitalize() if idx+1 < len(words) else ""
                            return f"{make} {model}".strip()
                        except:
                            return brand
        except Exception as e:
            print(f"⚠️ Strategy 2 (Heuristic) failed: {e}")
            
        return None
