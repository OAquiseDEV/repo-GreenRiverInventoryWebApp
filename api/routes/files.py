from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required
import os

bp = Blueprint('files', __name__)

@bp.route('/qr/<filename>', methods=['GET'])
@jwt_required()
def serve_qr_code(filename):
    """Serve QR code images"""
    file_path = f"/data/productos/etiquetas_qr/{filename}"

    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    return send_file(file_path, mimetype='image/png')

@bp.route('/manifiestos/<filename>', methods=['GET'])
def serve_manifest_pdf(filename):
    """
    Serve manifest PDFs.
    Public access for final manifests, JWT required for in-process manifests.
    """
    # Check if it's a final manifest (contains _final)
    if '_final' in filename:
        file_path = f"/data/manifiestos/finalizados/{filename}"
    else:
        file_path = f"/data/manifiestos/en_proceso/{filename}"

    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    return send_file(file_path, mimetype='application/pdf')
