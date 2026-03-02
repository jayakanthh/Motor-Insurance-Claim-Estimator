from __future__ import annotations

import io
from typing import Any, Dict, List, Optional
import os
import tempfile
import requests
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _ensure_unicode_font() -> Optional[str]:
    """
    Ensures a Unicode TTF font with the ₹ glyph is available and registered.
    Returns the registered font name, or None if unavailable.
    """
    font_name = "DejaVuSans"
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name

    try:
        cache_dir = os.path.join(tempfile.gettempdir(), "claimex_fonts")
        os.makedirs(cache_dir, exist_ok=True)
        ttf_path = os.path.join(cache_dir, "DejaVuSans.ttf")
        if not os.path.exists(ttf_path) or os.path.getsize(ttf_path) < 100_000:
            url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(ttf_path, "wb") as f:
                f.write(resp.content)
        pdfmetrics.registerFont(TTFont(font_name, ttf_path))
        return font_name
    except Exception:
        return None


def build_estimate_pdf(report: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Motor Insurance Claim Estimate",
    )

    styles = getSampleStyleSheet()
    # Try to use a Unicode font so ₹ renders correctly
    unicode_font = _ensure_unicode_font()
    if unicode_font:
        for key in ("Title", "Heading1", "Heading2", "BodyText", "Normal"):
            if key in styles:
                styles[key].fontName = unicode_font
    story: List[Any] = []

    # Helper to create wrapped paragraph cells
    def P(text: Any) -> Paragraph:
        s = str(text if text is not None else "")
        return Paragraph(xml_escape(s), styles["BodyText"])

    # Compute available width (points)
    avail_width = A4[0] - (18 * mm) - (18 * mm)
    def pct(w: float) -> float:
        return avail_width * w

    damage = (report or {}).get("damage_assessment", {}) or {}
    estimate = (report or {}).get("cost_estimate", {}) or {}
    summary = (estimate.get("summary", {}) or {})
    line_items = (estimate.get("line_items", []) or [])

    story.append(Paragraph("Motor Insurance Claim Estimate", styles["Title"]))
    story.append(Spacer(1, 10))

    vehicle_rows = [
        ["Registration", P(damage.get("registration_number", "Unknown"))],
        ["Vehicle", P(damage.get("car_info", "Unknown"))],
        ["Status", P(report.get("status", ""))],
    ]
    vt = Table(vehicle_rows, colWidths=[pct(0.30), pct(0.70)])
    vt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), unicode_font or "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
            ]
        )
    )
    story.append(vt)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Damages", styles["Heading2"]))
    damages = (damage.get("damages", []) or [])
    if not damages:
        story.append(Paragraph("No damages detected.", styles["BodyText"]))
        story.append(Spacer(1, 10))
    else:
        damage_table = [["Part", "Severity", "Description"]]
        for d in damages:
            damage_table.append(
                [
                    P(d.get("part", "")),
                    P(d.get("severity", "")),
                    P(d.get("description", "")),
                ]
            )
        dt = Table(damage_table, colWidths=[pct(0.25), pct(0.17), pct(0.58)])
        dt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), unicode_font or "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ]
            )
        )
        story.append(dt)
        story.append(Spacer(1, 12))

    story.append(Paragraph("Cost Summary (INR)", styles["Heading2"]))
    # If the Unicode font failed, fall back to 'INR ' prefix to avoid tofu
    rupee = "₹" if unicode_font else "INR "
    summary_rows = [
        ["Parts Total", P(f"{rupee}{summary.get('total_parts_cost', 0):,.2f}")],
        ["Labor", P(f"{rupee}{summary.get('total_labor_cost', 0):,.2f}")],
        ["Tax (GST)", P(f"{rupee}{summary.get('tax', 0):,.2f}")],
        ["Grand Total", P(f"{rupee}{summary.get('total_cost', 0):,.2f}")],
    ]
    st = Table(summary_rows, colWidths=[pct(0.40), pct(0.60)])
    st.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), unicode_font or "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
                ("FONTNAME", (0, -1), (-1, -1), unicode_font or "Helvetica"),
                ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
            ]
        )
    )
    story.append(st)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Line Items", styles["Heading2"]))
    if not line_items:
        story.append(Paragraph("No line items.", styles["BodyText"]))
    else:
        li_table = [["Part", "Severity", "Part Cost", "Labor", "Total", "Source"]]
        for it in line_items:
            li_table.append(
                [
                    P(it.get("part", "")),
                    P(it.get("severity", "")),
                    P(f"{rupee}{float(it.get('part_cost', 0) or 0):,.0f}"),
                    P(f"{rupee}{float(it.get('labor_cost', 0) or 0):,.0f}"),
                    P(f"{rupee}{float(it.get('total', 0) or 0):,.0f}"),
                    P(it.get("price_source", "")),
                ]
            )
        lt = Table(
            li_table,
            colWidths=[
                pct(0.22),  # Part
                pct(0.12),  # Severity
                pct(0.16),  # Part Cost
                pct(0.16),  # Labor
                pct(0.16),  # Total
                pct(0.18),  # Source
            ],
        )
        lt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("FONTNAME", (0, 0), (-1, 0), unicode_font or "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
                ]
            )
        )
        story.append(lt)

    doc.build(story)
    return buffer.getvalue()
