from api.app import db
from datetime import datetime

class Transformacion(db.Model):
    __tablename__ = 'transformaciones'

    id = db.Column(db.Integer, primary_key=True)
    producto_origen_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    producto_destino_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_transformacion = db.Column(db.String(100), nullable=False)
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'cantidad': float(self.cantidad) if self.cantidad else 0.0,
            'tipo_transformacion': self.tipo_transformacion,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_relations:
            if self.producto_origen:
                result['producto_origen'] = {
                    'id': self.producto_origen.id,
                    'nombre': self.producto_origen.nombre,
                    'cantidad_actual': float(self.producto_origen.cantidad) if self.producto_origen.cantidad else 0.0
                }
            if self.producto_destino:
                result['producto_destino'] = {
                    'id': self.producto_destino.id,
                    'nombre': self.producto_destino.nombre,
                    'cantidad_actual': float(self.producto_destino.cantidad) if self.producto_destino.cantidad else 0.0
                }
            if self.usuario:
                result['usuario'] = {
                    'id': self.usuario.id,
                    'nombre': self.usuario.nombre
                }

        return result

    def __repr__(self):
        return f'<Transformacion {self.tipo_transformacion}>'
