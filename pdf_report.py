"""
NeuroBiomeX PDF Report Generator
Generates a clinical PDF report using reportlab.
"""

import io
from datetime import date


def generate_pdf_report(patient_data: dict, scores: dict, recommendations: list) -> bytes:
    """
    Generate a clinical PDF report.

    Parameters:
        patient_data (dict): Patient info (name, patient_id, age, gender, …)
        scores (dict): Modality scores — values may be None if not analysed
        recommendations (list[str]): AI-generated clinical recommendations

    Returns:
        bytes: PDF content (falls back to plain text if reportlab unavailable)
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
        from reportlab.lib.enums import TA_RIGHT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm,  bottomMargin=2 * cm,
        )

        styles   = getSampleStyleSheet()
        indigo   = colors.HexColor("#6366f1")
        rose     = colors.HexColor("#f43f5e")
        slate    = colors.HexColor("#64748b")
        dark     = colors.HexColor("#1e293b")
        light_bg = colors.HexColor("#f8fafc")

        section_style = ParagraphStyle(
            "Section", parent=styles["Normal"],
            fontSize=9, fontName="Helvetica-Bold",
            textColor=indigo, spaceBefore=14, spaceAfter=6,
        )
        rec_style = ParagraphStyle(
            "Rec", parent=styles["Normal"],
            fontSize=9, fontName="Helvetica",
            textColor=dark, leading=13, spaceAfter=4, leftIndent=12,
        )
        disclaimer_style = ParagraphStyle(
            "Disc", parent=styles["Normal"],
            fontSize=7, fontName="Helvetica",
            textColor=colors.HexColor("#94a3b8"), leading=10,
        )

        story = []

        # ── Header ──────────────────────────────────────────────────────────
        header_data = [[
            Paragraph(
                '<font color="#6366f1" size="20"><b>NeuroBiome</b></font>'
                '<font color="#4f46e5" size="20"><b>X</b></font>',
                styles["Normal"],
            ),
            Paragraph(
                f'<font color="#64748b" size="9">'
                f'Date: {date.today().strftime("%B %d, %Y")}<br/>'
                f'Report ID: #NBX-{abs(hash(patient_data.get("patient_id","001"))) % 99999:05d}'
                f'</font>',
                ParagraphStyle("R", parent=styles["Normal"], alignment=TA_RIGHT, fontSize=9),
            ),
        ]]
        header_tbl = Table(header_data, colWidths=["60%", "40%"])
        header_tbl.setStyle(TableStyle([
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("LINEBELOW",   (0, 0), (-1,  0), 1.5, indigo),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 16))

        # ── Patient info ─────────────────────────────────────────────────────
        story.append(Paragraph("PATIENT INFORMATION", section_style))
        overall = patient_data.get("overall_risk", scores.get("overall"))
        risk_lbl = patient_data.get("risk_label", "N/A")
        pt_data = [
            ["Full Name",   patient_data.get("name", "N/A"),
             "Patient ID",  patient_data.get("patient_id", "N/A")],
            ["Age",         str(patient_data.get("age", "N/A")),
             "Gender",      patient_data.get("gender", "N/A")],
            ["Overall Risk", f"{overall:.1f}/100" if overall is not None else "Not analysed",
             "Risk Level",  risk_lbl],
        ]
        pt_tbl = Table(pt_data, colWidths=["22%", "28%", "22%", "28%"])
        pt_tbl.setStyle(TableStyle([
            ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME",  (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE",  (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), slate),
            ("TEXTCOLOR", (2, 0), (2, -1), slate),
            ("TEXTCOLOR", (1, 0), (1, -1), dark),
            ("TEXTCOLOR", (3, 0), (3, -1), dark),
            ("TEXTCOLOR", (1, 2), (1, 2), rose),
            ("TEXTCOLOR", (3, 2), (3, 2), rose),
            ("FONTNAME",  (1, 2), (1, 2), "Helvetica-Bold"),
            ("FONTNAME",  (3, 2), (3, 2), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [light_bg, colors.white]),
            ("GRID",      (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING",   (0, 0), (-1, -1), 6),
            ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(pt_tbl)
        story.append(Spacer(1, 14))

        # ── Modality scores ───────────────────────────────────────────────────
        story.append(Paragraph("MODALITY SCORES", section_style))

        def fmt(val):
            """Format a score or return 'Not analysed' when None."""
            return f"{val:.1f}%" if val is not None else "Not analysed"

        score_rows = [
            ["Modality",         "Score",                             "Status"],
            ["Microbiome",       fmt(scores.get("microbiome")),
             "Elevated" if scores.get("microbiome") and scores["microbiome"] >= 65 else ("—" if scores.get("microbiome") is None else "Normal")],
            ["Voice Biomarker",  fmt(scores.get("voice")),
             "Elevated" if scores.get("voice") and scores["voice"] >= 65 else ("—" if scores.get("voice") is None else "Normal")],
            ["Autonomic (HRV)",  fmt(scores.get("autonomic")),       "—" if scores.get("autonomic") is None else "Moderate"],
            ["Inflammation",     fmt(scores.get("inflammation")),    "—" if scores.get("inflammation") is None else "Elevated"],
            ["AMR Risk",         fmt(scores.get("amr")),             "—" if scores.get("amr") is None else "Moderate"],
        ]
        score_tbl = Table(score_rows, colWidths=["40%", "30%", "30%"])
        score_tbl.setStyle(TableStyle([
            ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, -1), 9),
            ("BACKGROUND",     (0, 0), (-1, 0), indigo),
            ("TEXTCOLOR",      (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [light_bg, colors.white]),
            ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN",          (1, 0), (2, -1), "CENTER"),
            ("PADDING",        (0, 0), (-1, -1), 6),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(score_tbl)
        story.append(Spacer(1, 14))

        # ── Recommendations ───────────────────────────────────────────────────
        story.append(Paragraph("AI-GENERATED CLINICAL RECOMMENDATIONS", section_style))
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"<b>{i:02d}.</b>  {rec}", rec_style))
        story.append(Spacer(1, 14))

        # ── Footer ────────────────────────────────────────────────────────────
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 8))
        story.append(Paragraph(
            "<b>Research Use Notice:</b> This report is generated by NeuroBiomeX for research, "
            "educational, and computational biology purposes only. It does not constitute a "
            "medical diagnosis, clinical decision, or professional medical advice. Always "
            "consult a qualified healthcare professional.",
            disclaimer_style,
        ))

        doc.build(story)
        return buffer.getvalue()

    except ImportError:
        return _fallback_text_report(patient_data, scores, recommendations)


# ── Plain-text fallback ───────────────────────────────────────────────────────

def _fallback_text_report(patient_data, scores, recommendations):
    def fmt(val):
        return f"{val:.1f}%" if val is not None else "Not analysed"

    lines = [
        "=" * 60,
        "  NeuroBiomeX — Clinical Intelligence Report",
        "=" * 60,
        "",
        f"Patient:  {patient_data.get('name', 'N/A')}",
        f"ID:       {patient_data.get('patient_id', 'N/A')}",
        f"Age:      {patient_data.get('age', 'N/A')}",
        f"Gender:   {patient_data.get('gender', 'N/A')}",
        "",
        "MODALITY SCORES",
        "-" * 40,
        f"Microbiome: {fmt(scores.get('microbiome'))}",
        f"Voice:      {fmt(scores.get('voice'))}",
        f"Autonomic:  {fmt(scores.get('autonomic'))}",
        f"Inflam.:    {fmt(scores.get('inflammation'))}",
        f"AMR:        {fmt(scores.get('amr'))}",
        "",
        "RECOMMENDATIONS",
        "-" * 40,
    ]
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i:02d}. {rec}")
    lines += [
        "",
        "=" * 60,
        "Research use only. Not a medical diagnosis.",
        "=" * 60,
    ]
    return "\n".join(lines).encode("utf-8")