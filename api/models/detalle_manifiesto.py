from api.app import db

class DetalleManifiesto(db.Model):
    __tablename__ = 'detalle_manifiesto'

    id = db.Column(db.Integer, primary_key=True)
    manifiesto_id = db.Column(db.Integer, db.ForeignKey('manifiestos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))

    def to_dict(self, include_relations=True):
        result = {
            'id': self.id,
            'cantidad': float(self.cantidad) if self.cantidad else 0.0,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'subtotal': float(self.subtotal) if self.subtotal else None
        }

        if include_relations and self.producto:
            result['producto'] = {
                'id': self.producto.id,
                'nombre': self.producto.nombre,
                'medida': self.producto.medida,
                'estado': self.producto.estado
            }

        return result

    def __repr__(self):
        return f'<DetalleManifiesto Manifiesto:{self.manifiesto_id} Producto:{self.producto_id}>'
