from api.app import db
from datetime import datetime

class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # qr_producto, barcode
    ruta_archivo = db.Column(db.String(500), nullable=False)
    formato = db.Column(db.String(10), default='png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'ruta_archivo': self.ruta_archivo,
            'formato': self.formato,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Etiqueta Producto:{self.producto_id} Tipo:{self.tipo}>'
