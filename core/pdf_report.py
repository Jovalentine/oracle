from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import os


def generate_forensic_pdf(result, save_path, storage_dir=""):
    styles = getSampleStyleSheet()
    story = []

    # =================================================
    # CUSTOM STYLES
    # =================================================

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=15,
        spaceBefore=12,
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=11,
        spaceAfter=8
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.grey
    )

    # =================================================
    # PAGE 1 — COVER
    # =================================================

    story.append(Paragraph("ORACLE FORENSIC SYSTEM", title_style))
    story.append(Paragraph(
        "AI-Assisted Accident Investigation Report",
        ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=13
        )
    ))

    story.append(Spacer(1, 30))

    # Safe Access to Case Data
    case_info = result.get("case", {})
    
    story.append(Paragraph(
        f"<b>Case ID:</b> {case_info.get('case_id', 'Unknown')}<br/>"
        f"<b>Generated At:</b> {case_info.get('generated_at', 'N/A')}<br/>"
        f"<b>System:</b> {case_info.get('system', 'Oracle Forensic v1.0')}",
        body_style
    ))

    story.append(Spacer(1, 20))

    story.append(Paragraph(
        case_info.get("disclaimer", "Automated Forensic Report"),
        small_style
    ))

    story.append(PageBreak())

    # =================================================
    # PAGE 2 — SCENE RECONSTRUCTION
    # =================================================

    story.append(Paragraph("1. Scene Reconstruction", section_style))

    scene = result.get("scene", {})
    story.append(Paragraph(
        scene.get("summary", "No summary available."),
        body_style
    ))

    story.append(Spacer(1, 10))

    scene_table = Table([
        ["Collision Type", scene.get("collision_type", "N/A")],
        ["Collision Overlap (IoU)", str(scene.get("collision_overlap", "N/A"))]
    ], colWidths=[2.5 * inch, 3.5 * inch])

    scene_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))

    story.append(scene_table)
    story.append(PageBreak())

    # =================================================
    # PAGE 3 — IDENTIFIED ENTITIES
    # =================================================

    story.append(Paragraph("2. Identified Vehicles", section_style))

    entities = result.get("entities", {})
    vehicles = entities.get("vehicles", [])

    if vehicles:
        vehicle_table_data = [["ID", "Type", "Fault %", "Confidence Reasoning"]]
        for v in vehicles:
            vehicle_table_data.append([
                v.get("id", "-"),
                v.get("type", "-"),
                f"{v.get('fault_percent', 0)}%",
                v.get("confidence_reason", "-")
            ])

        vehicle_table = Table(
            vehicle_table_data,
            colWidths=[1.2*inch, 1.2*inch, 1*inch, 2.6*inch]
        )

        vehicle_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ]))

        story.append(vehicle_table)
    else:
        story.append(Paragraph("No vehicles detected.", body_style))

    persons = entities.get("persons", [])
    if persons:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Identified Persons", section_style))

        person_table_data = [["ID", "Role", "Risk Level"]]
        for p in persons:
            person_table_data.append([
                p.get("id", "-"),
                p.get("role", "-"),
                p.get("risk_level", "-")
            ])

        person_table = Table(
            person_table_data,
            colWidths=[2*inch, 2*inch, 2*inch]
        )

        person_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
        ]))

        story.append(person_table)

    story.append(PageBreak())

    # =================================================
    # PAGE 4 — FORENSIC ANALYSIS
    # =================================================

    story.append(Paragraph("3. Forensic Analysis", section_style))

    analysis = result.get("analysis", {})
    fault = analysis.get("fault_allocation", {})
    severity = analysis.get("severity", {})
    risks = analysis.get("risk_factors", {})

    story.append(Paragraph(
        f"<b>Primary Responsible Vehicle:</b> "
        f"{fault.get('primary_vehicle', 'N/A')}<br/>"
        f"<b>Reasoning Method:</b> "
        f"{fault.get('method', 'N/A')}",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"<b>Accident Severity Score:</b> {severity.get('score', 0)} / 100<br/>"
        f"<b>Severity Level:</b> {severity.get('level', 'N/A')}",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Risk Factors:</b><br/>"
        f"- Pedestrian Involved: "
        f"{'Yes' if risks.get('pedestrian_involved') else 'No'}<br/>"
        f"- Multiple Vehicles: "
        f"{'Yes' if risks.get('multi_vehicle') else 'No'}",
        body_style
    ))

    # ✅ NEW: LICENSE PLATE TABLE FOR SINGLE IMAGE
    plates = analysis.get("license_plates", [])
    
    if plates:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Detected License Plates", section_style))

        plate_table_data = [["Plate Number", "Confidence"]]
        for p in plates:
            plate_table_data.append([
                p.get("plate", "UNKNOWN"),
                str(p.get("confidence", "N/A"))
            ])

        # Create table
        t = Table(plate_table_data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
        ]))
        story.append(t)

    story.append(PageBreak())

    # =================================================
    # PAGE 5 — VISUAL EVIDENCE
    # =================================================

    story.append(Paragraph("4. Visual Evidence", section_style))

    evidence = result.get("evidence", {})
    filename = evidence.get("annotated_image")
    
    # Path Resolution
    if filename:
        if storage_dir:
            annotated_path = os.path.join(storage_dir, filename)
        else:
            annotated_path = os.path.join("data", "outputs", filename)

        if os.path.exists(annotated_path):
            try:
                img = Image(
                    annotated_path,
                    width=6.5 * inch,
                    height=4.2 * inch
                )
                story.append(img)
            except Exception:
                story.append(Paragraph("[Image corrupted or format unsupported]", small_style))
        else:
            story.append(Paragraph("[Annotated image file not found]", small_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Annotated collision zones, vehicle identifiers, and entity markers "
        "generated by the Oracle Forensic AI.",
        body_style
    ))

    story.append(PageBreak())

    # =================================================
    # PAGE 6 — AI EXPLANATION
    # =================================================

    story.append(Paragraph("5. AI Investigative Explanation", section_style))
    story.append(Paragraph(result.get("explanation", "No explanation provided."), body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "— End of Forensic Report —",
        ParagraphStyle(
            "EndStyle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            textColor=colors.grey
        )
    ))

    # =================================================
    # BUILD PDF
    # =================================================

    doc = SimpleDocTemplate(
        save_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    doc.build(story)