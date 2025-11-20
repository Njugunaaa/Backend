from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from models import Event
from datetime import datetime
import pytz
import os
import tempfile

def get_today():
    tz = pytz.timezone('Africa/Nairobi')
    return datetime.now(tz).date()

def generate_events_pdf():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#7A030D'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#EB3237'),
        spaceAfter=12
    )
    
    elements.append(Paragraph("Church Events Calendar", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    today = get_today()
    upcoming_events = Event.query.filter(Event.date >= today).order_by(Event.date.asc()).all()
    past_events = Event.query.filter(Event.date < today).order_by(Event.date.desc()).all()
    
    elements.append(Paragraph("Upcoming Events", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if upcoming_events:
        for event in upcoming_events:
            event_data = [
                [Paragraph(f"<b>{event.title}</b>", styles['Normal'])],
                [Paragraph(f"Date: {event.date.strftime('%B %d, %Y')}", styles['Normal'])],
            ]
            
            if event.time:
                event_data.append([Paragraph(f"Time: {event.time.strftime('%I:%M %p')}", styles['Normal'])])
            if event.location:
                event_data.append([Paragraph(f"Location: {event.location}", styles['Normal'])])
            if event.description:
                event_data.append([Paragraph(f"{event.description[:200]}...", styles['Normal'])])
            
            event_table = Table(event_data, colWidths=[6*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FDF0D5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(event_table)
            elements.append(Spacer(1, 0.2*inch))
    else:
        elements.append(Paragraph("No upcoming events scheduled.", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Past Events", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if past_events:
        for event in past_events[:10]:
            event_data = [
                [Paragraph(f"<b>{event.title}</b>", styles['Normal'])],
                [Paragraph(f"Date: {event.date.strftime('%B %d, %Y')}", styles['Normal'])],
            ]
            
            if event.time:
                event_data.append([Paragraph(f"Time: {event.time.strftime('%I:%M %p')}", styles['Normal'])])
            if event.location:
                event_data.append([Paragraph(f"Location: {event.location}", styles['Normal'])])
            
            event_table = Table(event_data, colWidths=[6*inch])
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FDF0D5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            elements.append(event_table)
            elements.append(Spacer(1, 0.15*inch))
    else:
        elements.append(Paragraph("No past events.", styles['Normal']))
    
    doc.build(elements)
    return pdf_path
