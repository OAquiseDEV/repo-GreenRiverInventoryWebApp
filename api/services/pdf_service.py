from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
import base64
import io
from datetime import datetime

def decode_base64_image(base64_string):
    """
    Decode base64 image string to bytes.

    Args:
        base64_string: Base64 encoded image (with or without data:image prefix)

    Returns:
        BytesIO object containing image data
    """
    try:
        # Remove data:image/png;base64, prefix if present
        if 'base64,' in base64_string:
            base64_string = base64_string.split('base64,')[1]

        # Decode base64
        image_data = base64.b64decode(base64_string)
        return io.BytesIO(image_data)

    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

def generate_manifest_pdf(manifiesto, cliente, detalles, qr_code_path, output_path, is_final=False):
    """
    Generate PDF for delivery manifest.

    Args:
        manifiesto: Manifiesto object
        cliente: Cliente object
        detalles: List of DetalleManifiesto objects
        qr_code_path: Path to QR code image file
        output_path: Path where to save the PDF
        is_final: Boolean, True if generating final PDF with both signatures

    Returns:
        Boolean indicating success
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )

        # Container for PDF elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=6,
            alignment=TA_CENTER
        )

        # Header style
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12
        )

        # Normal style
        normal_style = styles['Normal']

        # ========== HEADER ==========
        # Company name
        company_name = Paragraph("GREEN RIVER POST", title_style)
        elements.append(company_name)

        # Document title with status badge
        if is_final:
            doc_title = Paragraph("MANIFIESTO DE ENTREGA - <font color='green'><b>ENTREGADO</b></font>", header_style)
        else:
            doc_title = Paragraph("MANIFIESTO DE ENTREGA", header_style)
        elements.append(doc_title)

        elements.append(Spacer(1, 0.2*inch))

        # ========== MANIFEST INFO ==========
        manifest_info = [
            ["<b>Número de Manifiesto:</b>", manifiesto.numero_manifiesto],
            ["<b>Fecha de Creación:</b>", manifiesto.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if manifiesto.fecha_creacion else "N/A"],
        ]

        if is_final and manifiesto.fecha_entrega:
            manifest_info.append(["<b>Fecha de Entrega:</b>", manifiesto.fecha_entrega.strftime("%Y-%m-%d %H:%M:%S")])

        manifest_info.append(["<b>Estado:</b>", manifiesto.estado.upper()])

        info_table = Table(manifest_info, colWidths=[2.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.2*inch))

        # ========== CLIENT INFO ==========
        client_header = Paragraph("<b>DATOS DEL CLIENTE</b>", header_style)
        elements.append(client_header)

        client_info = [
            ["<b>Nombre:</b>", cliente.nombre or "N/A"],
            ["<b>Dirección:</b>", cliente.direccion or "N/A"],
            ["<b>Teléfono:</b>", cliente.telefono or "N/A"],
            ["<b>Email:</b>", cliente.email or "N/A"],
            ["<b>RUC/DNI:</b>", cliente.ruc_dni or "N/A"],
        ]

        client_table = Table(client_info, colWidths=[2*inch, 4.5*inch])
        client_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(client_table)
        elements.append(Spacer(1, 0.3*inch))

        # ========== PRODUCTS TABLE ==========
        products_header = Paragraph("<b>PRODUCTOS</b>", header_style)
        elements.append(products_header)

        # Table headers
        table_data = [['Producto', 'Cantidad', 'Medida', 'Precio Unit.', 'Subtotal']]

        # Add products
        total = 0.0
        for detalle in detalles:
            producto = detalle.producto
            precio_unit = float(detalle.precio_unitario) if detalle.precio_unitario else 0.0
            subtotal = float(detalle.subtotal) if detalle.subtotal else 0.0
            total += subtotal

            table_data.append([
                producto.nombre,
                f"{float(detalle.cantidad):.2f}",
                producto.medida or "unidades",
                f"${precio_unit:.2f}" if precio_unit > 0 else "-",
                f"${subtotal:.2f}" if subtotal > 0 else "-"
            ])

        # Add total row if prices are present
        if total > 0:
            table_data.append(['', '', '', '<b>TOTAL:</b>', f'<b>${total:.2f}</b>'])

        products_table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        products_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2 if total > 0 else -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))

        if total > 0:
            # Style the total row
            products_table.setStyle(TableStyle([
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))

        elements.append(products_table)
        elements.append(Spacer(1, 0.3*inch))

        # ========== QR CODE ==========
        if os.path.exists(qr_code_path):
            qr_label = Paragraph("<b>CÓDIGO QR PARA VERIFICACIÓN:</b>", normal_style)
            elements.append(qr_label)
            elements.append(Spacer(1, 0.1*inch))

            qr_img = Image(qr_code_path, width=1.5*inch, height=1.5*inch)
            elements.append(qr_img)
            elements.append(Spacer(1, 0.3*inch))

        # ========== SIGNATURES ==========
        signatures_header = Paragraph("<b>FIRMAS</b>", header_style)
        elements.append(signatures_header)
        elements.append(Spacer(1, 0.1*inch))

        signature_data = []

        # Operator signature
        if manifiesto.firma_operador:
            sig_img_io = decode_base64_image(manifiesto.firma_operador)
            if sig_img_io:
                try:
                    op_sig_img = Image(sig_img_io, width=2*inch, height=1*inch)
                    signature_data.append(['<b>Firma Operador:</b>', op_sig_img])
                except:
                    signature_data.append(['<b>Firma Operador:</b>', '[Firma capturada]'])
            else:
                signature_data.append(['<b>Firma Operador:</b>', '[Firma capturada]'])
        else:
            signature_data.append(['<b>Firma Operador:</b>', '________________________'])

        # Client signature
        if is_final and manifiesto.firma_cliente:
            sig_img_io = decode_base64_image(manifiesto.firma_cliente)
            if sig_img_io:
                try:
                    client_sig_img = Image(sig_img_io, width=2*inch, height=1*inch)
                    signature_data.append(['<b>Firma Cliente:</b>', client_sig_img])
                except:
                    signature_data.append(['<b>Firma Cliente:</b>', '[Firma capturada]'])
            else:
                signature_data.append(['<b>Firma Cliente:</b>', '[Firma capturada]'])
        else:
            signature_data.append(['<b>Firma Cliente:</b>', '________________________'])

        sig_table = Table(signature_data, colWidths=[2*inch, 4*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(sig_table)

        # ========== FOOTER ==========
        elements.append(Spacer(1, 0.3*inch))
        footer_text = Paragraph(
            f"<font size=8>Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Sistema de Inventario Web - Nova</font>",
            ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        )
        elements.append(footer_text)

        # Build PDF
        doc.build(elements)

        return True

    except Exception as e:
        print(f"Error generating manifest PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
