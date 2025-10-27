import qrcode
import json
import os
from datetime import datetime
import secrets

def generate_codigo_qr(prefix="PROD"):
    """
    Generate a unique QR code identifier.

    Format: PREFIX-YYYYMMDDHHMMSS-XXXX
    Example: PROD-20250127143022-A7F3

    Args:
        prefix: Prefix for the code (PROD, MAN-QR, etc.)

    Returns:
        Unique codigo_qr string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_hex = secrets.token_hex(2).upper()  # 4 hex characters
    return f"{prefix}-{timestamp}-{random_hex}"

def generate_qr_image(content_data, file_path):
    """
    Generate QR code image and save to file.

    Args:
        content_data: Dictionary or string to encode in QR
        file_path: Full path where to save the PNG file

    Returns:
        Boolean indicating success
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Convert content to JSON string if it's a dict
        if isinstance(content_data, dict):
            qr_content = json.dumps(content_data)
        else:
            qr_content = str(content_data)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Generate image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to file
        img.save(file_path)

        return True

    except Exception as e:
        print(f"Error generating QR image: {e}")
        return False

def generate_product_qr(producto_id, codigo_qr, frontend_url="http://localhost:5173"):
    """
    Generate QR code for a product.

    Args:
        producto_id: ID of the product
        codigo_qr: Unique QR code string
        frontend_url: Base URL of the frontend

    Returns:
        Tuple (success, file_path)
    """
    # QR content
    qr_content = {
        "type": "producto",
        "id": producto_id,
        "codigo": codigo_qr,
        "url": f"{frontend_url}/productos/{producto_id}"
    }

    # File path
    file_path = f"/data/productos/etiquetas_qr/{codigo_qr}.png"

    # Generate image
    success = generate_qr_image(qr_content, file_path)

    return success, file_path if success else None

def generate_manifest_qr(numero_manifiesto, codigo_qr, frontend_url="http://localhost:5173"):
    """
    Generate QR code for a manifest.

    Args:
        numero_manifiesto: Manifest number
        codigo_qr: Unique QR code string
        frontend_url: Base URL of the frontend

    Returns:
        Tuple (success, file_path)
    """
    # QR content - URL for public verification
    qr_content = f"{frontend_url}/manifiestos/verificar?codigo={codigo_qr}"

    # File path
    file_path = f"/data/manifiestos/en_proceso/qr_{numero_manifiesto}.png"

    # Generate image
    success = generate_qr_image(qr_content, file_path)

    return success, file_path if success else None
