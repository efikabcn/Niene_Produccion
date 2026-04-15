"""
PDF Generator for Niene Produccion - Sauleda branding.
Generates professional PDF documents for each hoja (process sheet).
"""
import io
from datetime import date, time
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.platypus.flowables import Flowable


# ============================================
# Sauleda Brand Colors
# ============================================
SAULEDA_RED = HexColor("#b63221")
SAULEDA_DARK = HexColor("#8a2618")
SAULEDA_LIGHT = HexColor("#f5e6e3")
SAULEDA_GRAY = HexColor("#6b7280")
HEADER_BG = HexColor("#b63221")
SECTION_BG = HexColor("#8a2618")
ROW_ALT = HexColor("#faf5f4")
BORDER_COLOR = HexColor("#d1d5db")


# ============================================
# Custom Header Flowable
# ============================================
class SauledaHeader(Flowable):
    """Custom header with Sauleda branding."""

    def __init__(self, title, of_number, article_name=""):
        Flowable.__init__(self)
        self.title = title
        self.of_number = of_number
        self.article_name = article_name
        self.width = 170 * mm
        self.height = 32 * mm

    def draw(self):
        c = self.canv
        # Red header bar
        c.setFillColor(SAULEDA_RED)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)

        # Company name
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(12 * mm, self.height - 12 * mm, "SAULEDA")

        # Subtitle
        c.setFont("Helvetica", 9)
        c.drawString(12 * mm, self.height - 18 * mm, "Niene Produccio - Sistema de Gestio")

        # Document title - right side
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(self.width - 12 * mm, self.height - 12 * mm, self.title)

        # OF Number
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(self.width - 12 * mm, self.height - 20 * mm, "OF: " + self.of_number)

        # Article name
        if self.article_name:
            c.setFont("Helvetica", 8)
            c.drawRightString(self.width - 12 * mm, self.height - 27 * mm, self.article_name)


# ============================================
# Styles
# ============================================
def get_styles():
    """Get custom paragraph styles for Sauleda PDFs."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=white,
        backColor=SECTION_BG,
        spaceAfter=6,
        spaceBefore=12,
        leftIndent=6,
        rightIndent=6,
        leading=20,
    ))

    styles.add(ParagraphStyle(
        name='FieldLabel',
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=SAULEDA_GRAY,
        spaceAfter=1,
    ))

    styles.add(ParagraphStyle(
        name='FieldValue',
        fontName='Helvetica',
        fontSize=10,
        textColor=black,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='FooterText',
        fontName='Helvetica',
        fontSize=7,
        textColor=SAULEDA_GRAY,
        alignment=TA_CENTER,
    ))

    return styles


# ============================================
# Helper Functions
# ============================================
def fmt_date(d):
    """Format a date value."""
    if not d:
        return "-"
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d)


def fmt_time(t):
    """Format a time value."""
    if not t:
        return "-"
    if isinstance(t, time):
        return t.strftime("%H:%M")
    return str(t)


def fmt_bool(v):
    """Format a boolean value."""
    if v is None:
        return "-"
    return "Si" if v else "No"


def fmt_val(v):
    """Format any value."""
    if v is None:
        return "-"
    return str(v)


def make_field_row(fields, styles):
    """Create a row of label-value pairs as a table."""
    col_data = []
    col_styles = []
    for label, value in fields:
        col_data.append([
            Paragraph(label, styles['FieldLabel']),
            Paragraph(fmt_val(value), styles['FieldValue']),
        ])

    if not col_data:
        return Spacer(1, 1)

    # Build as a table with columns
    ncols = len(col_data)
    table_data = [
        [col_data[i][0] for i in range(ncols)],
        [col_data[i][1] for i in range(ncols)],
    ]

    col_widths = [170 * mm / ncols] * ncols
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, BORDER_COLOR),
    ]))
    return t


def make_data_table(headers, rows):
    """Create a formatted data table."""
    if not rows:
        return Spacer(1, 1)

    table_data = [headers] + rows
    ncols = len(headers)
    col_widths = [170 * mm / ncols] * ncols

    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), SAULEDA_RED),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    # Alternate row colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), ROW_ALT))

    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle(style_cmds))
    return t


def add_footer(canvas_obj, doc):
    """Add footer to each page."""
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 7)
    canvas_obj.setFillColor(SAULEDA_GRAY)
    canvas_obj.drawString(20 * mm, 10 * mm, "SAULEDA - Niene Produccio")
    canvas_obj.drawRightString(190 * mm, 10 * mm, "Pagina %d" % doc.page)
    canvas_obj.drawCentredString(105 * mm, 10 * mm, fmt_date(date.today()))
    canvas_obj.restoreState()


def build_pdf(story):
    """Build PDF from story elements and return bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer.getvalue()


# ============================================
# PDF Generators per Hoja
# ============================================
def generate_hoja2_pdf(hoja, of):
    """Generate PDF for Hoja 2 - Preparacio i Muntatge del Fil."""
    styles = get_styles()
    story = []

    story.append(SauledaHeader(
        "Preparacio i Muntatge del Fil",
        of.of_number,
        (of.codi_article or '') + ' - ' + (of.nom_article or ''),
    ))
    story.append(Spacer(1, 8 * mm))

    # Dades Generals
    story.append(Paragraph("Dades Generals", styles['SectionTitle']))
    story.append(make_field_row([
        ("Data", fmt_date(hoja.data)),
        ("Hora Inici", fmt_time(hoja.hora_inici_prep)),
        ("Hora Final", fmt_time(hoja.hora_final_prep)),
        ("Estat", fmt_val(hoja.estat)),
    ], styles))

    story.append(make_field_row([
        ("Responsable Preparacio", fmt_val(hoja.nom_resp_preparacio)),
        ("Fil Traspassat SLLP", fmt_bool(hoja.fil_traspassat_sllp)),
        ("Vores", fmt_bool(hoja.vores)),
        ("Condicions Bones", fmt_bool(hoja.cons_bones_condicions)),
    ], styles))

    # Verificacions
    story.append(Paragraph("Verificacions", styles['SectionTitle']))
    story.append(make_field_row([
        ("Telomares Panama", fmt_bool(hoja.telomares_panama)),
        ("Penelope", fmt_bool(hoja.penelope)),
        ("Fitxa Antiga", fmt_bool(hoja.fitxa_antiga)),
        ("Guia Montatge", fmt_bool(hoja.guia_montatge)),
    ], styles))
    story.append(make_field_row([
        ("Repas Conjunt", fmt_bool(hoja.repas_conjunt)),
    ], styles))

    # Responsables
    story.append(Paragraph("Responsables", styles['SectionTitle']))
    story.append(make_field_row([
        ("Muntar", fmt_val(hoja.responsables_muntar)),
        ("Desmuntar", fmt_val(hoja.responsables_desmuntar)),
        ("Ordidor Revisio", fmt_val(hoja.ordidor_revisio)),
    ], styles))

    # Muntada table
    if hoja.muntada and len(hoja.muntada) > 0:
        story.append(Paragraph("Muntada - Materials", styles['SectionTitle']))
        headers = ["Color", "Partida", "Proveidor", "N. Bulto", "Cons", "Pes (kg)"]
        rows = []
        for m in sorted(hoja.muntada, key=lambda x: x.ordre or 0):
            rows.append([
                fmt_val(m.color), fmt_val(m.partida), fmt_val(m.proveidor),
                fmt_val(m.n_bulto), fmt_val(m.conos), fmt_val(m.pes),
            ])
        story.append(make_data_table(headers, rows))

    # Observacions
    if hoja.observacions:
        story.append(Paragraph("Observacions", styles['SectionTitle']))
        story.append(Paragraph(str(hoja.observacions), styles['FieldValue']))

    return build_pdf(story)


def generate_hoja3_pdf(hoja, of):
    """Generate PDF for Hoja 3 - Fulla de Revisio: Ordida."""
    styles = get_styles()
    story = []

    story.append(SauledaHeader(
        "Fulla de Revisio: Ordida",
        of.of_number,
        (of.codi_article or '') + ' - ' + (of.nom_article or ''),
    ))
    story.append(Spacer(1, 8 * mm))

    # Dades Generals
    story.append(Paragraph("Dades Generals", styles['SectionTitle']))
    story.append(make_field_row([
        ("Data", fmt_date(hoja.data)),
        ("Estat", fmt_val(hoja.estat)),
    ], styles))

    # Hores
    story.append(Paragraph("Hores de Treball", styles['SectionTitle']))
    story.append(make_field_row([
        ("Hora Inici Ordir", fmt_time(hoja.hora_inici_ordir)),
        ("Hora Final Ordir", fmt_time(hoja.hora_final_ordir)),
        ("Hora Inici Plegar", fmt_time(hoja.hora_inici_plegar)),
        ("Hora Final Plegar", fmt_time(hoja.hora_final_plegar)),
    ], styles))

    # Tensions
    story.append(Paragraph("Tensions", styles['SectionTitle']))
    story.append(make_field_row([
        ("Tensio Ordit", fmt_val(hoja.tensio_ordit)),
        ("Tensio Plegat", fmt_val(hoja.tensio_plegat)),
        ("Producte No Conforme", fmt_bool(hoja.producte_no_conforme)),
        ("Quadra amb Fulla", fmt_bool(hoja.quadra_amb_fulla)),
    ], styles))

    # Responsables
    story.append(Paragraph("Responsables", styles['SectionTitle']))
    story.append(make_field_row([
        ("Responsable 1", fmt_val(hoja.responsable_1_nom)),
        ("Faixes R1", fmt_val(hoja.responsable_1_faixes)),
        ("Responsable 2", fmt_val(hoja.responsable_2_nom)),
        ("Faixes R2", fmt_val(hoja.responsable_2_faixes)),
    ], styles))

    # Verificacions
    story.append(Paragraph("Verificacions", styles['SectionTitle']))
    story.append(make_field_row([
        ("Fileta Neta", fmt_bool(hoja.fileta_neta)),
        ("Avanc Automatic", fmt_bool(hoja.avanc_automatic)),
        ("Valor Avanc", fmt_val(hoja.avanc_valor)),
        ("Fils Creuats", fmt_bool(hoja.fils_creuats)),
    ], styles))
    story.append(make_field_row([
        ("Revisat Passat Pua", fmt_bool(hoja.revisat_passat_pua)),
        ("Coincidir Mostra", fmt_bool(hoja.coincidir_mostra)),
        ("Mida Pua Igual", fmt_bool(hoja.mida_pua_igual)),
        ("Encarament Pua", fmt_bool(hoja.encarament_pua)),
    ], styles))
    story.append(make_field_row([
        ("Primer Fil Faixa", fmt_bool(hoja.primer_fil_faixa)),
    ], styles))

    # Observacions
    if hoja.observacions:
        story.append(Paragraph("Observacions", styles['SectionTitle']))
        story.append(Paragraph(str(hoja.observacions), styles['FieldValue']))

    return build_pdf(story)


def generate_hoja4_pdf(hoja, of):
    """Generate PDF for Hoja 4 - Col-locacio Plegador."""
    styles = get_styles()
    story = []

    story.append(SauledaHeader(
        "Col-locacio Plegador",
        of.of_number,
        (of.codi_article or '') + ' - ' + (of.nom_article or ''),
    ))
    story.append(Spacer(1, 8 * mm))

    # Dades Generals
    story.append(Paragraph("Dades Generals", styles['SectionTitle']))
    story.append(make_field_row([
        ("Data", fmt_date(hoja.data)),
        ("Hora", fmt_time(hoja.hora)),
        ("Num Teler", fmt_val(hoja.num_teler)),
        ("Estat", fmt_val(hoja.estat)),
    ], styles))

    # Plegador
    story.append(Paragraph("Plegador", styles['SectionTitle']))
    story.append(make_field_row([
        ("Num Ferro Plegador", fmt_val(hoja.num_ferro_plegador)),
        ("Color Plegador", fmt_val(hoja.color_plegador)),
        ("Verificar Colors", fmt_bool(hoja.verificar_colors)),
    ], styles))

    # Verificacions
    story.append(Paragraph("Verificacions", styles['SectionTitle']))
    story.append(make_field_row([
        ("Manquen Cargols", fmt_bool(hoja.manquen_cargols)),
        ("Cargols Reposats", fmt_bool(hoja.cargols_reposats)),
        ("Visualitzacio Optima", fmt_bool(hoja.visualitzacio_optim)),
    ], styles))

    # Valones
    story.append(Paragraph("Valones", styles['SectionTitle']))
    story.append(make_field_row([
        ("Posicio", fmt_val(hoja.posicio_valones)),
        ("Mida Baix", fmt_val(hoja.mida_valones_baix)),
        ("Mida Dalt", fmt_val(hoja.mida_valones_dalt)),
    ], styles))

    # Confirmacions
    story.append(Paragraph("Confirmacions", styles['SectionTitle']))
    story.append(make_field_row([
        ("Confirmat MGTZ", fmt_bool(hoja.confirmat_mgtz)),
        ("Confirmat Ordidor", fmt_bool(hoja.confirmat_ordidor)),
        ("Signatura Responsable", fmt_val(hoja.signatura_responsable)),
        ("Signatura Ordidor", fmt_val(hoja.signatura_ordidor)),
    ], styles))

    # Observacions
    if hoja.observacions:
        story.append(Paragraph("Observacions", styles['SectionTitle']))
        story.append(Paragraph(str(hoja.observacions), styles['FieldValue']))

    return build_pdf(story)


def generate_hoja5_pdf(hoja, of):
    """Generate PDF for Hoja 5 - Esquema de Montada."""
    styles = get_styles()
    story = []

    story.append(SauledaHeader(
        "Esquema de Montada",
        of.of_number,
        (of.codi_article or '') + ' - ' + (of.nom_article or ''),
    ))
    story.append(Spacer(1, 8 * mm))

    # Dades Generals
    story.append(Paragraph("Dades Generals", styles['SectionTitle']))
    story.append(make_field_row([
        ("Data", fmt_date(hoja.data)),
        ("Estat", fmt_val(hoja.estat)),
    ], styles))

    # Filades table
    if hoja.filades and len(hoja.filades) > 0:
        story.append(Paragraph("Filades", styles['SectionTitle']))
        headers = ["Quantitat", "Color", "Notes", "Total Acumulat"]
        rows = []
        for f in sorted(hoja.filades, key=lambda x: x.ordre or 0):
            rows.append([
                fmt_val(f.quantitat), fmt_val(f.color),
                fmt_val(f.notes), fmt_val(f.total_acumulat),
            ])
        story.append(make_data_table(headers, rows))

    # Observacions
    if hoja.observacions:
        story.append(Paragraph("Observacions", styles['SectionTitle']))
        story.append(Paragraph(str(hoja.observacions), styles['FieldValue']))

    return build_pdf(story)


def generate_hoja6_pdf(hoja, of):
    """Generate PDF for Hoja 6 - Programacio Passat de Pua."""
    styles = get_styles()
    story = []

    story.append(SauledaHeader(
        "Programacio Passat de Pua",
        of.of_number,
        (of.codi_article or '') + ' - ' + (of.nom_article or ''),
    ))
    story.append(Spacer(1, 8 * mm))

    # Dades Generals
    story.append(Paragraph("Dades Generals", styles['SectionTitle']))
    story.append(make_field_row([
        ("Data", fmt_date(hoja.data)),
        ("Nom Article", fmt_val(hoja.nom_article)),
        ("Total Fils", fmt_val(hoja.total_fils)),
        ("Estat", fmt_val(hoja.estat)),
    ], styles))

    # Config Passat Pua
    story.append(Paragraph("Configuracio Passat de Pua", styles['SectionTitle']))
    story.append(make_field_row([
        ("Faixes", fmt_val(hoja.passat_pua_faixes)),
        ("Pua (pall/cm)", fmt_val(hoja.pua_pallcm)),
        ("Fils per Pall", fmt_val(hoja.passat_fils_pall)),
    ], styles))

    # Calculated
    story.append(make_field_row([
        ("Total Fils Calculat", fmt_val(hoja.total_fils_calculat)),
        ("Total Ample (mm)", fmt_val(hoja.total_ample_mm)),
        ("Ample Valones (cm)", fmt_val(hoja.ample_valones_cm)),
        ("Eixamplament (mm)", fmt_val(hoja.eixamplament_mm)),
    ], styles))

    # Faixes table
    if hoja.faixes and len(hoja.faixes) > 0:
        story.append(Paragraph("Faixes", styles['SectionTitle']))
        headers = ["Tipus", "Fils", "Pallets", "Fan", "mm", "S'ha de passar"]
        rows = []
        for f in sorted(hoja.faixes, key=lambda x: x.ordre or 0):
            rows.append([
                fmt_val(f.tipus), fmt_val(f.fils), fmt_val(f.pallets),
                fmt_val(f.fan), fmt_val(f.mm), fmt_val(f.s_ha_de_passar),
            ])
        story.append(make_data_table(headers, rows))

    # Programacio table
    if hoja.programacio and len(hoja.programacio) > 0:
        story.append(Paragraph("Programacio", styles['SectionTitle']))
        headers = ["Tipus Faixa", "Fils", "Ample (mm)", "Observacio"]
        rows = []
        for p in sorted(hoja.programacio, key=lambda x: x.ordre or 0):
            rows.append([
                fmt_val(p.tipus_faixa), fmt_val(p.fils),
                fmt_val(p.ample_mm), fmt_val(p.observacio),
            ])
        story.append(make_data_table(headers, rows))

    # Observacions
    if hoja.observacions:
        story.append(Paragraph("Observacions", styles['SectionTitle']))
        story.append(Paragraph(str(hoja.observacions), styles['FieldValue']))

    return build_pdf(story)
