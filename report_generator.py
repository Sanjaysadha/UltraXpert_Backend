import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import inch
import csv
import shutil

def generate_medical_report_pdf(report_obj, patient_obj, doctor_full_name, file_path, enhanced_image_path=None, include_notes=True):
    """
    Generates a professional medical report PDF matching the specified UI design.
    """
    doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontSize=20, alignment=1, spaceAfter=20, textColor=colors.black
    )
    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=8, textColor=colors.HexColor("#2C3E50")
    )
    section_title_style = ParagraphStyle(
        'SectionTitleStyle', parent=styles['Heading3'], fontSize=12, spaceBefore=10, borderPadding=5, backColor=colors.HexColor("#F8F9FA")
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=10
    )
    label_style = ParagraphStyle(
        'LabelStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, leading=12
    )

    elements = []
    elements.append(Paragraph("Patient Report", title_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Header Card Simulation (Scan Image or Placeholder)
    if enhanced_image_path and os.path.exists(enhanced_image_path):
        try:
            img = Image(enhanced_image_path, width=5.0 * inch, height=3.0 * inch)
            img.hAlign = 'CENTER'
            elements.append(img)
        except Exception as e:
            elements.append(Paragraph(f"Image load Error: {str(e)}", body_style))
    else:
        # Better Placeholder for image
        placeholder_data = [[Paragraph("<font color='white' size='14'>SCAN IMAGE NOT AVAILABLE</font>", ParagraphStyle('PH', alignment=1))]]
        t_ph = Table(placeholder_data, colWidths=[5.0 * inch], rowHeights=[2.5 * inch])
        t_ph.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ROUNDEDCORNER', (0,0), (-1,-1), 16)
        ]))
        elements.append(t_ph)
    
    elements.append(Spacer(1, 0.1 * inch))
    # Subtitle with patient name/age/gender
    subtitle_text = f"<b>{patient_obj.name}</b><br/>{patient_obj.age or 'N/A'} yrs • {patient_obj.gender or 'N/A'} • {patient_obj.patient_identifier or 'N/A'}"
    elements.append(Paragraph(subtitle_text, ParagraphStyle('Subtitle', alignment=1, fontSize=12, leading=14)))
    
    elements.append(Spacer(1, 0.2 * inch))

    # Statistics Row (3 columns)
    stat_data = [
        [Paragraph("SCAN TYPE", label_style), Paragraph("MODALITY", label_style), Paragraph("BODY PART", label_style)],
        [Paragraph(f"<b>{report_obj.scan_type or 'N/A'}</b>", body_style), Paragraph(f"<b>{report_obj.modality or 'N/A'}</b>", body_style), Paragraph(f"<b>{report_obj.body_part or 'Unknown'}</b>", body_style)]
    ]
    stat_table = Table(stat_data, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.Whiter(colors.lightgrey, 0.9)),
        ('ROUNDEDCORNER', (0,0), (-1,-1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Scan Information Card
    elements.append(Paragraph("Scan Information", header_style))
    
    scan_details = [
        [Paragraph("Referring Doctor", label_style), Paragraph(f"<b>{doctor_full_name}</b>", body_style)],
        [Paragraph("Scan Date & Time", label_style), Paragraph(f"<b>{report_obj.created_at.strftime('%Y-%m-%d %I:%M %p') if report_obj.created_at else 'N/A'}</b>", body_style)],
        [Paragraph("Report Status", label_style), Paragraph(f"<font color='green'><b>{report_obj.status}</b></font>", body_style)],
    ]
    
    details_table = Table(scan_details, colWidths=[2.5 * inch, 3.5 * inch])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.Whiter(colors.grey, 0.8)),
    ]))
    elements.append(details_table)

    if include_notes:
        elements.append(Paragraph("Findings", section_title_style))
        elements.append(Paragraph(report_obj.findings or "Scan enhanced and processed successfully.", body_style))

        elements.append(Paragraph("Impression", section_title_style))
        elements.append(Paragraph(report_obj.impression or "Enhanced scan available.", body_style))

        elements.append(Paragraph("Recommendations", section_title_style))
        elements.append(Paragraph(report_obj.recommendations or "Clinical correlation recommended.", body_style))

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Generated by UltraXpert on {datetime.now().strftime('%Y-%m-%d %H:%M')}", label_style))

    doc.build(elements)


def generate_medical_report_csv(report_obj, patient_obj, doctor_full_name, file_path, include_notes=True):
    """Generates a CSV export of the report."""
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Report ID", report_obj.id])
        writer.writerow(["Patient ID", patient_obj.patient_identifier])
        writer.writerow(["Patient Name", patient_obj.name])
        writer.writerow(["Age", patient_obj.age])
        writer.writerow(["Gender", patient_obj.gender])
        writer.writerow(["Referring Doctor", doctor_full_name])
        writer.writerow(["Scan Type", report_obj.scan_type])
        writer.writerow(["Modality", report_obj.modality])
        writer.writerow(["Body Part", report_obj.body_part])
        writer.writerow(["Created At", report_obj.created_at.isoformat() if report_obj.created_at else "N/A"])
        
        if include_notes:
            writer.writerow(["Findings", report_obj.findings])
            writer.writerow(["Impression", report_obj.impression])
            writer.writerow(["Recommendations", report_obj.recommendations])

def generate_medical_report_jpeg(enhanced_image_path, file_path, include_notes=True, patient_name="N/A"):
    """
    Exports the enhanced scanning image as a JPEG.
    """
    if enhanced_image_path and os.path.exists(enhanced_image_path):
        shutil.copy(enhanced_image_path, file_path)
    else:
        # Create a simple text-based mock if no image exists (no Pillow dependency)
        with open(file_path, "wb") as f:
            f.write(f"MOCK_JPEG_IMAGE_FOR_{patient_name}\n".encode())
            f.write(b"No enhanced scan image available.")

def generate_medical_report_dicom(report_obj, patient_obj, enhanced_image_path, file_path, include_notes=True):
    """
    Generates a structured medical data file (Simulated DICOM).
    Actual DICOM requires pydicom and pixel data handling.
    """
    with open(file_path, "wb") as f:
        # Structured header
        f.write(b"DICOM_STRUCTURED_DATA_V1.0\n")
        f.write(f"PatientName: {patient_obj.name}\n".encode())
        f.write(f"PatientID: {patient_obj.patient_identifier}\n".encode())
        f.write(f"Age: {patient_obj.age}\n".encode())
        f.write(f"Gender: {patient_obj.gender}\n".encode())
        f.write(f"Modality: {report_obj.modality}\n".encode())
        f.write(f"ScanType: {report_obj.scan_type}\n".encode())
        f.write(f"BodyPart: {report_obj.body_part}\n".encode())
        
        if include_notes:
            f.write(f"Findings: {report_obj.findings}\n".encode())
            f.write(f"Impression: {report_obj.impression}\n".encode())
            f.write(f"Recommendations: {report_obj.recommendations}\n".encode())
        
        f.write(b"IMAGE_DATA_START\n")
        if enhanced_image_path and os.path.exists(enhanced_image_path):
            with open(enhanced_image_path, "rb") as img_f:
                f.write(img_f.read())
        else:
            f.write(b"NO_IMAGE_DATA")
        f.write(b"\nIMAGE_DATA_END")
