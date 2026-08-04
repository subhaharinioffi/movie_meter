import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate the total page count and add headers/footers dynamically.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#6D001A")) # Deep Maroon
        
        # Header (Skip first page for cover look)
        if self._pageNumber > 1:
            self.drawString(54, 750, "MOVIE METER – Technical Documentation & Architecture Report")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b")) # Slate Gray
        self.drawString(54, 32, "© 2026 Movie Meter Platform. All Rights Reserved.")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(filename="Movie_Meter_Documentation.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles matching Vercel/Apple SaaS branding
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor("#6D001A"), # Deep Maroon
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#475569"), # Slate
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#6D001A"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=8
    )
    
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#6D001A"),
    )
    
    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("MOVIE METER", title_style))
    story.append(Paragraph("AI-Powered IMDb Rating Category Predictor & Success Analytics Platform", subtitle_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Metadata block
    meta_data = [
        [Paragraph("<b>Document Type:</b> Technical Architecture & Design Document", body_style)],
        [Paragraph("<b>Target Domain:</b> South Indian Cinema & OTT Distribution Strategy", body_style)],
        [Paragraph("<b>Author:</b> Machine Learning Engineer & Software Architect", body_style)],
        [Paragraph("<b>Model Version:</b> v2.0 (XGBoost Classifier)", body_style)],
        [Paragraph("<b>Date:</b> August 4, 2026", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[400])
    t_meta.setStyle(TableStyle([
        ('LINELEFT', (0,0), (-1,-1), 3, colors.HexColor("#6D001A")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
    ]))
    story.append(t_meta)
    story.append(PageBreak())
    
    # ------------------ SECTION 1 ------------------
    story.append(Paragraph("1. Executive Summary & Problem Statement", h1_style))
    story.append(Paragraph(
        "In the commercial film industry, particularly within South Indian regional cinema, pre-production planning and budget allocations are frequently based on subjective intuition. Over-investment or improper distribution negotiations can lead to severe capital losses for production houses and OTT networks.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Movie Meter</b> is an enterprise-grade machine learning platform designed to predict a film's quality category (High, Medium, or Low) using pre-release metadata (genres, runtime, language, content certification, and target casting reputation metrics). By mapping superstar and director popularity coefficients in a leak-free out-of-fold manner, the platform provides distribution matching, revenue estimation ranges, and demographic projections before theatrical release.",
        body_style
    ))
    
    # ------------------ SECTION 2 ------------------
    story.append(Paragraph("2. Technical Pipeline & Feature Engineering", h1_style))
    story.append(Paragraph(
        "The model is trained on a merged and cleaned database of 4,900+ films. The pipeline strictly excludes post-release parameters (such as actual ticketing revenues, review texts, or voter counts) to prevent data leakage.",
        body_style
    ))
    
    story.append(Paragraph("2.1 Reputation Mappings & Target Encoding", h2_style))
    story.append(Paragraph(
        "High-cardinality nominal parameters like <i>director_name</i> and <i>actor_1_name</i> pose severe challenges to traditional one-hot encoders. To resolve this, our preprocessor computes cross-validated out-of-fold target averages for IMDb scores. The average rating achieved by a director or actor's previous works serves as a continuous numerical score mapping. For new or fictional projects (e.g., Nelson Dilipkumar or Superstar Vijay), historical weights are calculated on startup to simulate prediction outcomes accurately.",
        body_style
    ))
    
    story.append(Paragraph("2.2 Preprocessing Details", h2_style))
    story.append(Paragraph(
        "Runtimes are parsed and cleaned of empty fields using median values, while content certification labels are bucketed into clean categories (e.g. PG-13, R, G). High skew features are scaled using standard normalization to prevent gradient boosting scaling biases.",
        body_style
    ))
    
    # ------------------ SECTION 3 ------------------
    story.append(Paragraph("3. Model Selection & Hyperparameter Tuning", h1_style))
    story.append(Paragraph(
        "A rigorous model selection process compared four primary algorithms using 5-Fold Stratified Cross-Validation to assess classification boundaries:",
        body_style
    ))
    
    # Comparison table
    comp_data = [
        ["Model Architecture", "CV Accuracy", "ROC-AUC", "LogLoss", "Status"],
        ["Extreme Gradient Boosting (XGBoost)", "62.1%", "73.0%", "0.85", "Best / Selected"],
        ["Random Forest Classifier", "60.4%", "71.2%", "0.89", "Baseline"],
        ["Gradient Boosting Machine (GBM)", "59.8%", "70.1%", "0.91", "Baseline"],
        ["Logistic Regression (Baseline)", "54.2%", "64.0%", "1.05", "Discarded"]
    ]
    t_comp = Table(comp_data, colWidths=[180, 75, 75, 75, 90])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#6D001A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))
    story.append(PageBreak())
    
    # ------------------ SECTION 4 ------------------
    story.append(Paragraph("4. Streamlit SaaS Redesign & Architecture", h1_style))
    story.append(Paragraph(
        "The web application frontend has been redesigned to align with premium SaaS platforms (Vercel, Apple, Stripe):",
        body_style
    ))
    
    ui_points = [
        "<b>Single-Page Smooth Scrolling:</b> Replaced the heavy tabbed structure with a single-page scrolling layout where sections are stacked vertically. This guarantees fluid transitions and prevents layout lag.",
        "<b>Sticky Anchor Links Navigation:</b> A custom navigation bar remains fixed at the top of the window, providing responsive shortcut buttons that smooth-scroll to specific sections.",
        "<b>High Contrast Input Rendering:</b> Overrode all Streamlit widget labels to render in bold dark slate (#0f172a). Input textboxes and select options are styled in clean white panels to prevent light-theme rendering bugs on browser dark-mode defaults.",
        "<b>Plotly Success Analytics:</b> Integrates dynamic, responsive gauges showing success probabilities, market potentials, and production readiness index models."
    ]
    for pt in ui_points:
        story.append(Paragraph(f"• {pt}", body_style))
        
    # ------------------ SECTION 5 ------------------
    story.append(Paragraph("5. Revenue Projections & Distribution Strategy", h1_style))
    story.append(Paragraph(
        "Understanding rating predictions in isolation is insufficient for commercial stakeholders. The platform translates prediction results into financial projections and release recommendations:",
        body_style
    ))
    
    story.append(Paragraph("5.1 Gross Box Office Projection Model", h2_style))
    story.append(Paragraph(
        "Using starcast reputation averages and target genres as multiplier coefficients, gross revenues are projected across international (USD) and regional South Indian (INR Crores) markets. These estimates are mapped against standard industry budgets to define a projected ROI percentage boundaries window.",
        body_style
    ))
    
    story.append(Paragraph("5.2 Digital OTT Licensing Windows", h2_style))
    story.append(Paragraph(
        "Based on classifications (High/Medium/Low success potential), the model recommends optimal post-theatrical streaming platforms (e.g. Netflix for high crossover titles; Hotstar for regional action; Sun NXT for indie/low-budget titles) and lists guidelines for release scheduling.",
        body_style
    ))
    
    # Callout Box
    story.append(Spacer(1, 10))
    c_text = [
        [Paragraph("<b>Operational Guideline:</b> The theatrical exclusive window must be maintained at a minimum of 4-6 weeks for South Indian theater chains to maximize local box office yields, before shifting to digital streaming platforms.", callout_style)]
    ]
    t_callout = Table(c_text, colWidths=[480])
    t_callout.setStyle(TableStyle([
        ('LINELEFT', (0,0), (-1,-1), 4, colors.HexColor("#FFD54F")),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fffde7")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_callout)
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)

if __name__ == "__main__":
    build_pdf()
    print("PDF Generation complete.")
