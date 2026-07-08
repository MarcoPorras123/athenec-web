# Athenec

> Soluciones tecnológicas, asesoría académica y equipamiento para impulsar tus ideas.

Athenec es una plataforma que unifica tres líneas de negocio bajo una misma marca:

1. **Soluciones Tecnológicas** — Desarrollo de software a medida (web, móvil, automatizaciones, integraciones y sistemas empresariales).
2. **Asesoría e Investigación Metodológica** — Acompañamiento para tesis, papers y proyectos académicos, incluyendo diseño metodológico, análisis estadístico y redacción científica.
3. **Venta de Equipos Tecnológicos** — Comercialización de hardware, periféricos y equipamiento para estudiantes, profesionales y empresas.

---

## Tabla de contenidos

- [Stack tecnológico](#stack-tecnológico)
- [Estructura del monorepo](#estructura-del-monorepo)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Endpoints de la API](#endpoints-de-la-api)
- [Variables de entorno](#variables-de-entorno)
- [Roadmap](#roadmap)
- [Licencia](#licencia)

---

## Stack tecnológico

| Capa           | Tecnología                                        |
| -------------- | ------------------------------------------------- |
| Frontend       | HTML5 semántico + Tailwind CSS (vía CDN)          |
| Backend        | Python 3.11+, FastAPI, Uvicorn                    |
| Validación     | Pydantic v2                                       |
| ORM            | SQLAlchemy 2.x                                    |
| Base de datos  | SQLite (dev) → PostgreSQL / AWS RDS (prod)        |
| Config         | python-dotenv                                     |
| Despliegue     | Docker-ready · AWS (EC2 / ECS / Lambda + RDS)     |
| Control código | Git + GitHub                                      |

---

## Estructura del monorepo

```
athenec/
├── .gitignore
├── .env.example
├── README.md
├── frontend/
│   ├── index.html
│   └── css/
│       └── styles.css
└── backend/
    ├── requirements.txt
    ├── main.py
    └── routers/
        ├── __init__.py
        └── soluciones.py
```

---

## Requisitos previos

- **Python** 3.11 o superior
- **pip** (viene con Python)
- **Git**
- Navegador moderno (Chrome, Firefox, Edge, Safari)

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/athenec.git
cd athenec
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita el archivo .env con tus valores locales
```

### 3. Backend — crear entorno virtual e instalar dependencias

```bash
cd backend
python -m venv venv

# Activar el entorno:
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Frontend

No requiere build. Tailwind se carga vía CDN. Basta con abrir `frontend/index.html` en el navegador o servirlo con cualquier servidor estático.

---

## Ejecución

### Levantar el backend (API)

Desde la carpeta `backend/` con el entorno virtual activo:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API disponible en: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- Documentación alternativa (ReDoc): `http://localhost:8000/redoc`

### Servir el frontend

Opción rápida:

```bash
cd frontend
python -m http.server 5173
```

Abre `http://localhost:5173` en tu navegador.

---

## Endpoints de la API

Base URL: `http://localhost:8000/api`

### Salud del servicio

| Método | Ruta      | Descripción                     |
| ------ | --------- | ------------------------------- |
| GET    | `/`       | Mensaje raíz de bienvenida.     |
| GET    | `/health` | Estado del servicio (`ok`).     |

### Soluciones Tecnológicas

#### `POST /api/soluciones/cotizar`

Recibe una solicitud de cotización para un proyecto de software.

**Request body (JSON):**

```json
{
  "nombre_cliente": "María Pérez",
  "correo": "maria@example.com",
  "tipo_proyecto": "web",
  "descripcion": "Necesito una tienda online con pasarela de pagos."
}
```

**Campos:**

| Campo            | Tipo    | Requerido | Descripción                                          |
| ---------------- | ------- | --------- | ---------------------------------------------------- |
| `nombre_cliente` | string  | Sí        | Nombre completo del solicitante.                     |
| `correo`         | string  | Sí        | Email válido de contacto.                            |
| `tipo_proyecto`  | string  | Sí        | `web`, `movil`, `automatizacion`, `integracion`, etc |
| `descripcion`    | string  | Sí        | Detalle del proyecto (mín. 10 caracteres).           |

**Respuesta exitosa (201 Created):**

```json
{
  "success": true,
  "message": "Cotización recibida correctamente. Te contactaremos pronto.",
  "ticket_id": "COT-20260708-001",
  "data": {
    "nombre_cliente": "María Pérez",
    "correo": "maria@example.com",
    "tipo_proyecto": "web",
    "descripcion": "Necesito una tienda online con pasarela de pagos."
  }
}
```

**Errores comunes:**

- `422 Unprocessable Entity` — Fallo de validación de Pydantic (campos faltantes o inválidos).

---

## Variables de entorno

Ver `.env.example` en la raíz del proyecto. Variables clave:

- `ENVIRONMENT` — `development` | `staging` | `production`
- `API_HOST`, `API_PORT` — Host y puerto del servidor.
- `DATABASE_URL` — Cadena de conexión SQLAlchemy.
- `FRONTEND_ORIGIN` — Orígenes permitidos para CORS (separados por coma).
- `SECRET_KEY` — Clave para firmar tokens.

---

## Roadmap

- [ ] Módulo de asesoría de tesis (formulario + gestión de sesiones).
- [ ] Catálogo de equipos con carrito y checkout.
- [ ] Panel de administración.
- [ ] Autenticación JWT.
- [ ] Notificaciones por correo (SMTP / SES).
- [ ] Despliegue en AWS con Terraform.
- [ ] Migración a PostgreSQL en RDS.

---

## Licencia

Propietario. © Athenec. Todos los derechos reservados.
