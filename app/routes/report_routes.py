import os
from datetime import datetime
from io import BytesIO

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.db import get_cursor
from app.utils.encryption import decrypt_context

load_dotenv()

router = APIRouter()


def generate_medical_report(user_data: dict, context_data: dict) -> str:
    """
    Genera un informe médico usando Gemini basado en los datos del usuario y su contexto.
    """
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

    prompt = f"""
Eres un psicólogo profesional especializado en salud mental. 
Genera un informe médico psicológico detallado y profesional basado en la siguiente información del paciente:

Información del Paciente:
- Nombre: {user_data["name"]}
- Edad: {user_data["age"]} años
- Ciudad: {user_data["city"]}
- Email: {user_data["email"]}

Contexto del Paciente:
{context_data}

INSTRUCCIONES IMPORTANTES:
1. Escribe un informe médico profesional en español
2. Incluye las siguientes secciones:
   - MOTIVO DE CONSULTA (infiere basado en el contexto)
   - OBSERVACIONES CLÍNICAS
   - EVALUACIÓN PSICOLÓGICA
   - ANÁLISIS DEL CONTEXTO PERSONAL
   - RECOMENDACIONES TERAPÉUTICAS
   - CONCLUSIONES
3. Usa un tono profesional y empático
4. Considera el contexto cultural colombiano
5. Sé específico y detallado basándote en la información proporcionada
6. Si falta información, indícalo pero haz las mejores inferencias posibles

FORMATO DEL TEXTO:
- NO repitas los datos del paciente (nombre, edad, ciudad, email) porque ya aparecen en el encabezado del documento
- NO incluyas líneas como "Paciente:" o "Fecha:" al inicio del informe
- Escribe los títulos de secciones en MAYÚSCULAS sin usar asteriscos ni markdown
- Escribe el texto corrido en párrafos normales SIN usar asteriscos dobles (**)
- NO uses formato markdown (**, *, #, etc.)
- Usa solamente texto plano con títulos en MAYÚSCULAS y contenido en texto normal
- Escribe listas con guiones simples (-)

Genera el informe completo comenzando directamente con la primera sección:
"""

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generando informe con Gemini: {str(e)}"
        )


def create_pdf_report(
    user_data: dict, context_data: dict, report_content: str
) -> BytesIO:
    """
    Crea un PDF profesional con el informe médico.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch
    )

    # Estilos
    styles = getSampleStyleSheet()

    # Estilo personalizado para el título
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a5490"),
        spaceAfter=30,
        alignment=1,  # Centrado
        fontName="Helvetica-Bold",
    )

    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    )

    # Estilo para el cuerpo del texto
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        spaceAfter=10,
        alignment=4,  # Justificado
    )

    # Contenido del PDF
    story = []

    # Encabezado
    story.append(Paragraph("INFORME MÉDICO PSICOLÓGICO", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Información del documento
    fecha_actual = datetime.now().strftime("%d de %B de %Y")
    info_data = [
        ["Fecha de Emisión:", fecha_actual],
        ["Código de Paciente:", f"PSI-{user_data['id']:06d}"],
    ]

    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 0.3 * inch))

    # Línea separadora
    line_data = [["" for _ in range(1)]]
    line_table = Table(line_data, colWidths=[6.5 * inch])
    line_table.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor("#1a5490")),
            ]
        )
    )
    story.append(line_table)
    story.append(Spacer(1, 0.2 * inch))

    # Datos del paciente
    story.append(Paragraph("DATOS DEL PACIENTE", subtitle_style))
    patient_data = [
        ["Nombre:", user_data["name"]],
        ["Edad:", f"{user_data['age']} años"],
        ["Ciudad:", user_data["city"]],
        ["Email:", user_data["email"]],
    ]

    patient_table = Table(patient_data, colWidths=[1.5 * inch, 5 * inch])
    patient_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(patient_table)
    story.append(Spacer(1, 0.3 * inch))

    # Contenido del informe generado por IA
    # Procesar el texto del informe
    lines = report_content.split("\n")
    
    # Filtrar líneas que repiten información del encabezado
    skip_patterns = [
        "**paciente:**",
        "**fecha:**",
        "paciente:",
        "fecha:",
        "nombre:",
        "edad:",
        "ciudad:",
        "email:",
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1 * inch))
            continue
        
        # Saltar líneas que repiten información del encabezado
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in skip_patterns):
            # Si la línea contiene solo el patrón y la información (ej: "Paciente: Juan"), saltarla
            if len(line) < 150:  # Las líneas de metadatos suelen ser cortas
                continue
        
        # Limpiar cualquier formato markdown que pueda haber quedado
        clean_line = line.replace("**", "").replace("##", "").replace("#", "")
        
        # Detectar títulos (líneas en mayúsculas completas)
        if clean_line.isupper() and len(clean_line) < 100 and len(clean_line) > 3:
            # Línea en mayúsculas (probablemente un título de sección)
            story.append(Paragraph(clean_line, subtitle_style))
        else:
            # Texto normal - limpiar el formato
            story.append(Paragraph(clean_line, body_style))

    story.append(Spacer(1, 0.5 * inch))

    # Pie de página con advertencia
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["BodyText"],
        fontSize=8,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=1,
        italic=True,
    )

    story.append(Spacer(1, 0.3 * inch))
    story.append(line_table)
    story.append(Spacer(1, 0.1 * inch))
    story.append(
        Paragraph(
            "Este informe es confidencial y está destinado exclusivamente para uso médico profesional.",
            footer_style,
        )
    )
    story.append(
        Paragraph(
            "Generado automáticamente por el Sistema de Apoyo Psicológico - No reemplaza una evaluación profesional presencial.",
            footer_style,
        )
    )

    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


@router.get("/users/{user_id}/report")
def generate_user_report(user_id: int):
    """
    Genera un informe médico en PDF basado en el contexto del usuario.

    Args:
        user_id: ID del usuario

    Returns:
        PDF con el informe médico
    """
    cur = get_cursor()

    # Obtener datos del usuario y su contexto
    cur.execute(
        "SELECT id, email, name, age, city, context, encrypted FROM users WHERE id = %s",
        (user_id,),
    )
    user_row = cur.fetchone()

    if not user_row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_data = {
        "id": user_row[0],
        "email": user_row[1],
        "name": user_row[2],
        "age": user_row[3],
        "city": user_row[4],
    }

    context_data = user_row[5]
    encrypted = user_row[6]

    if not context_data:
        raise HTTPException(status_code=404, detail="Contexto de usuario no encontrado")

    if encrypted:
        context_data = decrypt_context(context_data)

    # Generar el contenido del informe con IA
    report_content = generate_medical_report(user_data, context_data)

    # Crear el PDF
    pdf_buffer = create_pdf_report(user_data, context_data, report_content)

    # Nombre del archivo
    filename = f"informe_psicologico_{user_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
