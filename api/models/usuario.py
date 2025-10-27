from api.app import db
from datetime import datetime
import bcrypt

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    productos = db.relationship('Producto', foreign_keys='Producto.created_by', backref='creator', lazy='dynamic')
    movimientos = db.relationship('Movimiento', backref='usuario', lazy='dynamic')
    transformaciones = db.relationship('Transformacion', backref='usuario', lazy='dynamic')
    manifiestos_creados = db.relationship('Manifiesto', foreign_keys='Manifiesto.usuario_creador_id', backref='creator', lazy='dynamic')
    manifiestos_entregados = db.relationship('Manifiesto', foreign_keys='Manifiesto.usuario_entrega_id', backref='delivery_user', lazy='dynamic')

    def set_password(self, password):
        """Hash password using bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_role=True):
        result = {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_role and self.role:
            result['role'] = self.role.to_dict()
        return result

    def __repr__(self):
        return f'<Usuario {self.email}>'
