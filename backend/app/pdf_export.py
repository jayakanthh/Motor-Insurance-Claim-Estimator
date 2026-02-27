from __future__ import annotations

import io
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


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
    story: List[Any] = []

    damage = (report or {}).get("damage_assessment", {}) or {}
    estimate = (report or {}).get("cost_estimate", {}) or {}
    summary = (estimate.get("summary", {}) or {})
    line_items = (estimate.get("line_items", []) or [])

    story.append(Paragraph("Motor Insurance Claim Estimate", styles["Title"]))
    story.append(Spacer(1, 10))

    vehicle_rows = [
        ["Registration", str(damage.get("registration_number", "Unknown"))],
        ["Vehicle", str(damage.get("car_info", "Unknown"))],
        ["Status", str(report.get("status", ""))],
    ]
    vt = Table(vehicle_rows, colWidths=[40 * mm, 140 * mm])
    vt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
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
                    str(d.get("part", "")),
                    str(d.get("severity", "")),
                    str(d.get("description", "")),
                ]
            )
        dt = Table(damage_table, colWidths=[42 * mm, 25 * mm, 113 * mm])
        dt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(dt)
        story.append(Spacer(1, 12))

    story.append(Paragraph("Cost Summary (INR)", styles["Heading2"]))
    summary_rows = [
        ["Parts Total", f"₹{summary.get('total_parts_cost', 0):,.2f}"],
        ["Labor", f"₹{summary.get('total_labor_cost', 0):,.2f}"],
        ["Tax (GST)", f"₹{summary.get('tax', 0):,.2f}"],
        ["Grand Total", f"₹{summary.get('total_cost', 0):,.2f}"],
    ]
    st = Table(summary_rows, colWidths=[60 * mm, 120 * mm])
    st.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
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
                    str(it.get("part", "")),
                    str(it.get("severity", "")),
                    f"₹{float(it.get('part_cost', 0) or 0):,.0f}",
                    f"₹{float(it.get('labor_cost', 0) or 0):,.0f}",
                    f"₹{float(it.get('total', 0) or 0):,.0f}",
                    str(it.get("price_source", "")),
                ]
            )
        lt = Table(li_table, colWidths=[36 * mm, 18 * mm, 24 * mm, 22 * mm, 22 * mm, 58 * mm])
        lt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(lt)

    doc.build(story)
    return buffer.getvalue()

