from api.app import db

# Import all models for easy access
from api.models.role import Role
from api.models.usuario import Usuario
from api.models.categoria import Categoria
from api.models.cliente import Cliente
from api.models.producto import Producto
from api.models.movimiento import Movimiento
from api.models.transformacion import Transformacion
from api.models.manifiesto import Manifiesto
from api.models.detalle_manifiesto import DetalleManifiesto
from api.models.etiqueta import Etiqueta

__all__ = [
    'db',
    'Role',
    'Usuario',
    'Categoria',
    'Cliente',
    'Producto',
    'Movimiento',
    'Transformacion',
    'Manifiesto',
    'DetalleManifiesto',
    'Etiqueta'
]
