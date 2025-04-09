# pdf_generator.py
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus import PageBreak, ListFlowable, ListItem

from models import CallSheet, Location, CastMember, CrewMember

def generate_call_sheet_pdf(call_sheet: CallSheet, output_path: str) -> bool:
    """
    Generate a PDF call sheet from a CallSheet object
    
    Args:
        call_sheet: The CallSheet object to generate PDF from
        output_path: Path to save the generated PDF
        
    Returns:
        bool: True if PDF generation was successful, False otherwise
    """
    try:
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Create custom styles
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='Heading3',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
        
        styles.add(ParagraphStyle(
            name='Bold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10
        ))
        
        # Start building document content
        story = []
        
        # Add logo if available
        if call_sheet.logo_path and os.path.exists(call_sheet.logo_path):
            try:
                img = Image(call_sheet.logo_path, width=1.5*inch, height=1*inch)
                img.hAlign = 'RIGHT'
                story.append(img)
                story.append(Spacer(1, 0.25*inch))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Add title
        production_date_str = call_sheet.production_date.strftime("%A, %B %d, %Y")
        title_text = f"<b>{call_sheet.production_name.upper()}</b><br/><b>CALL SHEET - {production_date_str}</b>"
        story.append(Paragraph(title_text, styles['Title']))
        story.append(Spacer(1, 0.25*inch))
        
        # Add general call time
        call_time_text = f"<b>GENERAL CALL TIME: {call_sheet.general_call_time.strftime('%I:%M %p')}</b>"
        story.append(Paragraph(call_time_text, styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        
        # Add home base
        if call_sheet.home_base:
            home_base_text = f"<b>HOME BASE:</b><br/>{call_sheet.home_base.name}<br/>{call_sheet.home_base.address}"
            if call_sheet.home_base.notes:
                home_base_text += f"<br/><i>Notes: {call_sheet.home_base.notes}</i>"
            story.append(Paragraph(home_base_text, styles['Normal']))
            story.append(Spacer(1, 0.25*inch))
        
        # Add filming locations
        if call_sheet.filming_locations:
            story.append(Paragraph("<b>FILMING LOCATIONS:</b>", styles['Heading3']))
            
            for i, location in enumerate(call_sheet.filming_locations, 1):
                loc_text = f"<b>Location {i}: {location.name}</b><br/>{location.address}"
                if location.notes:
                    loc_text += f"<br/><i>Notes: {location.notes}</i>"
                story.append(Paragraph(loc_text, styles['Normal']))
            
            story.append(Spacer(1, 0.25*inch))
        
        # Add cast list
        if call_sheet.cast_members:
            story.append(Paragraph("<b>CAST:</b>", styles['Heading2']))
            
            # Create table for cast
            cast_data = [["Name", "Role", "Call Time"]]
            
            # Sort cast by call time
            sorted_cast = sorted(call_sheet.cast_members, key=lambda x: x.call_time)
            
            for cast in sorted_cast:
                cast_data.append([
                    cast.name,
                    cast.role,
                    cast.call_time.strftime("%I:%M %p")
                ])
            
            # Create table with style
            cast_table = Table(cast_data, colWidths=[2.5*inch, 2.5*inch, 1*inch])
            cast_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            
            story.append(cast_table)
            story.append(Spacer(1, 0.25*inch))
            
            # Add cast notes
            cast_with_notes = [c for c in call_sheet.cast_members if c.notes]
            if cast_with_notes:
                story.append(Paragraph("<b>CAST NOTES:</b>", styles['Heading3']))
                
                for cast in cast_with_notes:
                    note_text = f"<b>{cast.name} ({cast.role}):</b> {cast.notes}"
                    story.append(Paragraph(note_text, styles['Normal']))
                
                story.append(Spacer(1, 0.25*inch))
        
        # Add crew list
        if call_sheet.crew_members:
            story.append(Paragraph("<b>CREW:</b>", styles['Heading2']))
            
            # Group crew by department
            departments = call_sheet.get_departments()
            
            for department in departments:
                story.append(Paragraph(f"<b>{department.upper()}</b>", styles['Heading3']))
                
                # Create table for this department
                crew_data = [["Name", "Position", "Call Time"]]
                
                # Get crew in this department and sort by call time
                dept_crew = sorted(
                    call_sheet.get_crew_by_department(department),
                    key=lambda x: x.call_time
                )
                
                for crew in dept_crew:
                    crew_data.append([
                        crew.name,
                        crew.position,
                        crew.call_time.strftime("%I:%M %p")
                    ])
                
                # Create table with style
                crew_table = Table(crew_data, colWidths=[2*inch, 3*inch, 1*inch])
                crew_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                
                story.append(crew_table)
                story.append(Spacer(1, 0.25*inch))
            
            # Add crew notes
            crew_with_notes = [c for c in call_sheet.crew_members if c.notes]
            if crew_with_notes:
                story.append(Paragraph("<b>CREW NOTES:</b>", styles['Heading3']))
                
                for crew in crew_with_notes:
                    note_text = f"<b>{crew.name} ({crew.position}):</b> {crew.notes}"
                    story.append(Paragraph(note_text, styles['Normal']))
                
                story.append(Spacer(1, 0.25*inch))
        
        # Add general notes
        if call_sheet.notes:
            story.append(Paragraph("<b>PRODUCTION NOTES:</b>", styles['Heading3']))
            story.append(Paragraph(call_sheet.notes, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return True
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

def preview_call_sheet(call_sheet: CallSheet) -> None:
    """
    Generate a temporary PDF preview of the call sheet and open it
    
    Args:
        call_sheet: The CallSheet object to preview
    """
    import tempfile
    import os
    import subprocess
    import platform
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_path = temp_file.name
    
    # Generate PDF
    success = generate_call_sheet_pdf(call_sheet, temp_path)
    
    if success:
        # Open PDF with default viewer
        if platform.system() == 'Windows':
            os.startfile(temp_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', temp_path])
        else:  # Linux
            subprocess.call(['xdg-open', temp_path])
    else:
        print("Failed to generate PDF preview.")
