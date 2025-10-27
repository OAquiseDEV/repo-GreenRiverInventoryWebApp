from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from api.models import db, Movimiento, Manifiesto, Producto, Categoria, Usuario
from api.utils.decorators import role_required
from api.services.excel_service import generate_movements_excel, generate_deliveries_excel
from datetime import datetime
import os

bp = Blueprint('reportes', __name__)

@bp.route('/movimientos', methods=['GET'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def generate_movements_report():
    """Generate movements report in Excel format"""
    # Get filters
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    producto_id = request.args.get('producto_id', type=int)
    tipo = request.args.get('tipo')

    # Build query with joins
    query = db.session.query(
        Movimiento.id,
        Movimiento.created_at,
        Producto.nombre.label('producto'),
        Categoria.nombre.label('categoria'),
        Movimiento.tipo,
        Movimiento.cantidad,
        Usuario.nombre.label('usuario'),
        Movimiento.observaciones
    ).join(
        Producto, Movimiento.producto_id == Producto.id
    ).join(
        Categoria, Producto.categoria_id == Categoria.id
    ).join(
        Usuario, Movimiento.usuario_id == Usuario.id
    )

    # Apply filters
    if fecha_desde:
        query = query.filter(Movimiento.created_at >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Movimiento.created_at <= fecha_hasta)

    if producto_id:
        query = query.filter(Movimiento.producto_id == producto_id)

    if tipo:
        query = query.filter(Movimiento.tipo == tipo)

    # Order by date descending
    query = query.order_by(Movimiento.created_at.desc())

    # Execute query
    results = query.all()

    # Convert to list of dictionaries
    data = []
    for row in results:
        data.append({
            'Fecha': row.created_at.strftime('%Y-%m-%d %H:%M:%S') if row.created_at else '',
            'Producto': row.producto,
            'Categoría': row.categoria,
            'Tipo': row.tipo,
            'Cantidad': float(row.cantidad) if row.cantidad else 0.0,
            'Usuario': row.usuario,
            'Observaciones': row.observaciones or ''
        })

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"movimientos_{timestamp}.xlsx"
    output_path = f"/data/reportes/movimientos/{filename}"

    # Generate Excel
    success = generate_movements_excel(data, output_path)

    if not success:
        return jsonify({"error": "Error generando reporte"}), 500

    # Return file
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/entregas', methods=['GET'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def generate_deliveries_report():
    """Generate deliveries (manifests) report in Excel format"""
    # Get filters
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado')

    # Build query
    from api.models import Cliente

    query = db.session.query(
        Manifiesto.numero_manifiesto,
        Cliente.nombre.label('cliente'),
        Manifiesto.estado,
        Manifiesto.fecha_creacion,
        Manifiesto.fecha_entrega,
        Usuario.nombre.label('creado_por')
    ).join(
        Cliente, Manifiesto.cliente_id == Cliente.id
    ).join(
        Usuario, Manifiesto.usuario_creador_id == Usuario.id
    )

    # Apply filters
    if fecha_desde:
        query = query.filter(Manifiesto.fecha_creacion >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Manifiesto.fecha_creacion <= fecha_hasta)

    if cliente_id:
        query = query.filter(Manifiesto.cliente_id == cliente_id)

    if estado:
        query = query.filter(Manifiesto.estado == estado)

    # Order by date descending
    query = query.order_by(Manifiesto.fecha_creacion.desc())

    # Execute query
    results = query.all()

    # Convert to list of dictionaries
    data = []
    for row in results:
        data.append({
            'Número Manifiesto': row.numero_manifiesto,
            'Cliente': row.cliente,
            'Estado': row.estado,
            'Fecha Creación': row.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if row.fecha_creacion else '',
            'Fecha Entrega': row.fecha_entrega.strftime('%Y-%m-%d %H:%M:%S') if row.fecha_entrega else '',
            'Creado Por': row.creado_por
        })

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"entregas_{timestamp}.xlsx"
    output_path = f"/data/reportes/entregas/{filename}"

    # Generate Excel
    success = generate_deliveries_excel(data, output_path)

    if not success:
        return jsonify({"error": "Error generando reporte"}), 500

    # Return file
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@bp.route('/inventario', methods=['GET'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def generate_inventory_report():
    """Generate current inventory snapshot report"""
    # Get all products with their categories
    query = db.session.query(
        Producto.nombre,
        Categoria.nombre.label('categoria'),
        Producto.estado,
        Producto.cantidad,
        Producto.medida
    ).join(
        Categoria, Producto.categoria_id == Categoria.id
    ).order_by(
        Categoria.nombre.asc(),
        Producto.nombre.asc()
    )

    results = query.all()

    # Convert to list of dictionaries
    data = []
    for row in results:
        data.append({
            'Producto': row.nombre,
            'Categoría': row.categoria,
            'Estado': row.estado,
            'Cantidad': float(row.cantidad) if row.cantidad else 0.0,
            'Medida': row.medida or 'unidades'
        })

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"inventario_{timestamp}.xlsx"
    output_path = f"/data/reportes/movimientos/{filename}"

    # Use movements excel generator (same format)
    success = generate_movements_excel(data, output_path)

    if not success:
        return jsonify({"error": "Error generando reporte"}), 500

    # Return file
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
