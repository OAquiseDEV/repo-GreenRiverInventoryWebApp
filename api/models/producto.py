from api.app import db
from datetime import datetime
from decimal import Decimal

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    medida = db.Column(db.String(50))
    estado = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    codigo_qr = db.Column(db.String(255), unique=True)
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    movimientos = db.relationship('Movimiento', backref='producto', lazy='dynamic')
    etiqueta = db.relationship('Etiqueta', backref='producto', uselist=False)
    transformaciones_origen = db.relationship('Transformacion', foreign_keys='Transformacion.producto_origen_id', backref='producto_origen', lazy='dynamic')
    transformaciones_destino = db.relationship('Transformacion', foreign_keys='Transformacion.producto_destino_id', backref='producto_destino', lazy='dynamic')
    detalles_manifiesto = db.relationship('DetalleManifiesto', backref='producto', lazy='dynamic')

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'nombre': self.nombre,
            'medida': self.medida,
            'estado': self.estado,
            'cantidad': float(self.cantidad) if self.cantidad else 0.0,
            'codigo_qr': self.codigo_qr,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_relations:
            if self.categoria:
                result['categoria'] = self.categoria.to_dict()
            if self.cliente:
                result['cliente'] = self.cliente.to_dict()
            if self.etiqueta:
                result['etiqueta'] = self.etiqueta.to_dict()

        return result

    def __repr__(self):
        return f'<Producto {self.nombre}>'
