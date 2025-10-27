from api.app import db
from datetime import datetime

class Movimiento(db.Model):
    __tablename__ = 'movimientos'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, salida, ajuste
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'tipo': self.tipo,
            'cantidad': float(self.cantidad) if self.cantidad else 0.0,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_relations:
            if self.producto:
                result['producto'] = {
                    'id': self.producto.id,
                    'nombre': self.producto.nombre
                }
            if self.usuario:
                result['usuario'] = {
                    'id': self.usuario.id,
                    'nombre': self.usuario.nombre
                }

        return result

    def __repr__(self):
        return f'<Movimiento {self.tipo} - {self.cantidad}>'
