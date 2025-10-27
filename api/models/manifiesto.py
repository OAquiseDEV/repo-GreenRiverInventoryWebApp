from api.app import db
from datetime import datetime

class Manifiesto(db.Model):
    __tablename__ = 'manifiestos'

    id = db.Column(db.Integer, primary_key=True)
    numero_manifiesto = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='en_proceso')  # en_proceso, en_transito, entregado, cancelado
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime)
    codigo_qr = db.Column(db.String(255), unique=True)
    firma_operador = db.Column(db.Text)
    firma_cliente = db.Column(db.Text)
    pdf_path_proceso = db.Column(db.String(500))
    pdf_path_final = db.Column(db.String(500))
    usuario_creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_entrega_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    detalles = db.relationship('DetalleManifiesto', backref='manifiesto', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'numero_manifiesto': self.numero_manifiesto,
            'estado': self.estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'codigo_qr': self.codigo_qr,
            'firma_operador': self.firma_operador,
            'firma_cliente': self.firma_cliente,
            'pdf_path_proceso': self.pdf_path_proceso,
            'pdf_path_final': self.pdf_path_final,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_relations:
            if self.cliente:
                result['cliente'] = self.cliente.to_dict()
            if self.creator:
                result['usuario_creador'] = {
                    'id': self.creator.id,
                    'nombre': self.creator.nombre
                }
            if self.delivery_user:
                result['usuario_entrega'] = {
                    'id': self.delivery_user.id,
                    'nombre': self.delivery_user.nombre
                }
            result['detalles'] = [detalle.to_dict(include_relations=True) for detalle in self.detalles]
            result['total_productos'] = self.detalles.count()

        return result

    def __repr__(self):
        return f'<Manifiesto {self.numero_manifiesto}>'
