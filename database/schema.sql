-- Sistema de Inventario Web - Nova
-- Database Schema
-- PostgreSQL 14+

-- Drop tables if they exist (for clean initialization)
DROP TABLE IF EXISTS etiquetas CASCADE;
DROP TABLE IF EXISTS detalle_manifiesto CASCADE;
DROP TABLE IF EXISTS manifiestos CASCADE;
DROP TABLE IF EXISTS transformaciones CASCADE;
DROP TABLE IF EXISTS movimientos CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- Table 1: roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table 2: usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_role_id ON usuarios(role_id);

-- Table 3: categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table 4: clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion TEXT,
    ruc_dni VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_clientes_email ON clientes(email);
CREATE INDEX idx_clientes_ruc_dni ON clientes(ruc_dni);

-- Table 5: productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    categoria_id INTEGER NOT NULL REFERENCES categorias(id),
    medida VARCHAR(50),
    estado VARCHAR(50) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL DEFAULT 0,
    cliente_id INTEGER REFERENCES clientes(id),
    codigo_qr VARCHAR(255) UNIQUE,
    created_by INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_productos_categoria_id ON productos(categoria_id);
CREATE INDEX idx_productos_estado ON productos(estado);
CREATE UNIQUE INDEX idx_productos_codigo_qr ON productos(codigo_qr);
CREATE INDEX idx_productos_cliente_id ON productos(cliente_id);

-- Table 6: movimientos
CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    tipo VARCHAR(20) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    observaciones TEXT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_movimientos_producto_id ON movimientos(producto_id);
CREATE INDEX idx_movimientos_tipo ON movimientos(tipo);
CREATE INDEX idx_movimientos_created_at ON movimientos(created_at);

-- Table 7: transformaciones
CREATE TABLE transformaciones (
    id SERIAL PRIMARY KEY,
    producto_origen_id INTEGER NOT NULL REFERENCES productos(id),
    producto_destino_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad DECIMAL(10,2) NOT NULL,
    tipo_transformacion VARCHAR(100) NOT NULL,
    observaciones TEXT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transformaciones_producto_origen_id ON transformaciones(producto_origen_id);
CREATE INDEX idx_transformaciones_producto_destino_id ON transformaciones(producto_destino_id);
CREATE INDEX idx_transformaciones_created_at ON transformaciones(created_at);

-- Table 8: manifiestos
CREATE TABLE manifiestos (
    id SERIAL PRIMARY KEY,
    numero_manifiesto VARCHAR(50) UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'en_proceso',
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_entrega TIMESTAMP,
    codigo_qr VARCHAR(255) UNIQUE,
    firma_operador TEXT,
    firma_cliente TEXT,
    pdf_path_proceso VARCHAR(500),
    pdf_path_final VARCHAR(500),
    usuario_creador_id INTEGER NOT NULL REFERENCES usuarios(id),
    usuario_entrega_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_manifiestos_numero_manifiesto ON manifiestos(numero_manifiesto);
CREATE INDEX idx_manifiestos_cliente_id ON manifiestos(cliente_id);
CREATE INDEX idx_manifiestos_estado ON manifiestos(estado);
CREATE INDEX idx_manifiestos_fecha_creacion ON manifiestos(fecha_creacion);

-- Table 9: detalle_manifiesto
CREATE TABLE detalle_manifiesto (
    id SERIAL PRIMARY KEY,
    manifiesto_id INTEGER NOT NULL REFERENCES manifiestos(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2)
);

CREATE INDEX idx_detalle_manifiesto_manifiesto_id ON detalle_manifiesto(manifiesto_id);
CREATE INDEX idx_detalle_manifiesto_producto_id ON detalle_manifiesto(producto_id);

-- Table 10: etiquetas
CREATE TABLE etiquetas (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER UNIQUE NOT NULL REFERENCES productos(id),
    tipo VARCHAR(20) NOT NULL,
    ruta_archivo VARCHAR(500) NOT NULL,
    formato VARCHAR(10) DEFAULT 'png',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_etiquetas_producto_id ON etiquetas(producto_id);

-- SEED DATA

-- Insert roles
INSERT INTO roles (nombre, descripcion) VALUES
    ('Administrador', 'Acceso completo al sistema'),
    ('Oficina', 'Gestión de productos, manifiestos y reportes'),
    ('Operario', 'Transformación de productos y preparación de manifiestos'),
    ('Delivery', 'Ejecución de entregas'),
    ('Cliente', 'Confirmación de entregas y firma');

-- Insert admin user (password: changeme123, hashed with bcrypt)
-- Note: In production, this password should be changed immediately
-- The hash below is for: changeme123
INSERT INTO usuarios (nombre, email, password_hash, role_id, activo) VALUES
    ('Administrador', 'admin@greenriver.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyWUIvdgXN9i', 1, TRUE);

-- Insert sample categories
INSERT INTO categorias (nombre, descripcion) VALUES
    ('Madera', 'Productos de madera y derivados'),
    ('Metal', 'Productos metálicos y aleaciones'),
    ('Plástico', 'Productos plásticos y polímeros'),
    ('Químico', 'Productos químicos y sustancias'),
    ('Textil', 'Productos textiles y telas');

-- Insert sample clients for testing
INSERT INTO clientes (nombre, email, telefono, direccion, ruc_dni) VALUES
    ('ABC Industries', 'contacto@abcindustries.com', '555-1234', 'Av. Principal 123', '20123456789'),
    ('XYZ Corp', 'info@xyzcorp.com', '555-5678', 'Calle Comercio 456', '20987654321'),
    ('Green Solutions', 'ventas@greensolutions.com', '555-9012', 'Jr. Industrial 789', '20456789123');

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_productos_updated_at BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_manifiestos_updated_at BEFORE UPDATE ON manifiestos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
