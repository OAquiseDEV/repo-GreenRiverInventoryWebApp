# Sistema de Inventario Web - Nova

Sistema completo de gestión de inventario con trazabilidad mediante códigos QR, firmas digitales y reportes automáticos para Green River Post.

## Características Principales

- **Gestión de Productos**: Registro manual con generación automática de códigos QR
- **Transformaciones**: Cambio de estado de productos (No terminado → Terminado)
- **Manifiestos de Entrega**: Generación de PDFs con firmas digitales de operario y cliente
- **Verificación Pública**: Los clientes pueden confirmar entregas escaneando QR
- **Reportes Automáticos**: Generación de reportes en Excel y PDF
- **Control de Acceso**: 5 roles de usuario con permisos específicos

## Tecnologías

### Backend
- Python 3.10+ con Flask 3.x
- PostgreSQL 14+
- SQLAlchemy, JWT, QRCode, ReportLab, Pandas

### Frontend
- React 18 + Vite 5
- TailwindCSS 3
- React Router, Axios

### Infraestructura
- Docker & Docker Compose
- Nginx + Gunicorn

## Instalación Rápida

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd repo-GreenRiverInventoryWebApp

# 2. Configurar ambiente
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar con Docker
docker-compose up --build -d

# 4. Acceder
# Frontend: http://localhost:5173
# Backend: http://localhost:5000/api
```

## Credenciales Iniciales

- **Email**: admin@greenriver.com
- **Contraseña**: changeme123

⚠️ **Cambiar inmediatamente después del primer acceso**

## Estructura del Proyecto

```
repo-GreenRiverInventoryWebApp/
├── api/                    # Backend Flask
│   ├── models/            # SQLAlchemy models (10 tablas)
│   ├── routes/            # API endpoints
│   ├── services/          # QR, PDF, Excel generation
│   └── app.py
├── src/                   # Frontend React
│   ├── components/
│   ├── pages/
│   └── contexts/
├── database/
│   └── schema.sql         # PostgreSQL schema + seed data
├── data/                  # Generated files (QR, PDF, reports)
├── docker-compose.yml
└── README.md
```

## Documentación Completa

Ver `planning.md` para:
- Especificaciones completas de API
- Workflows end-to-end
- Esquema de base de datos detallado
- Guía de despliegue

## Roles y Permisos

| Rol | Permisos |
|-----|----------|
| Administrador | Acceso total |
| Oficina | Productos, manifiestos, reportes |
| Operario | Transformaciones |
| Delivery | Entregas |
| Cliente | Confirmación vía QR |

## Desarrollo Local

```bash
# Backend
cd api
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
export DATABASE_URL="postgresql://user:pass@localhost:5432/inventory_nova"
flask run

# Frontend
npm install
npm run dev
```

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f backend

# Reiniciar servicio
docker-compose restart backend

# Acceder a PostgreSQL
docker-compose exec db psql -U inventory_user -d inventory_nova

# Backup
docker-compose exec db pg_dump -U inventory_user inventory_nova > backup.sql
```

## Contacto

**Desarrollador**: Oscar Aquise Falcon
**Cliente**: Green River Post
**Versión**: 1.0