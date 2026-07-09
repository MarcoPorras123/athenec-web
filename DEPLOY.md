# Athenec - Guia de despliegue

Esta guia cubre 3 rutas para llevar Athenec a produccion, ordenadas de menor a mayor complejidad.

---

## 1. Local con Docker Compose (prueba rapida)

Requisitos: Docker Desktop instalado.

```bash
cd athenec-web
cp .env.example .env
# Edita .env: pon un ADMIN_TOKEN aleatorio y credenciales SMTP si quieres correos reales
docker compose up -d --build
```

- Frontend: `http://localhost/`
- Backend / Swagger: `http://localhost:8000/docs`
- Admin: `http://localhost/admin.html`

Comandos utiles:
```bash
docker compose logs -f backend      # ver logs en vivo
docker compose exec backend sh      # abrir shell en el contenedor
docker compose down                  # apagar
docker compose down -v               # apagar y borrar volumen (base de datos)
```

La base SQLite se persiste en el volumen nombrado `athenec_data`.

---

## 2. AWS App Runner (mas simple, ~15 min)

App Runner es "PaaS": empujas la imagen y AWS se encarga de escalar, TLS y balanceo.

### Paso a paso

1. **Crear repositorios ECR** (uno por servicio):
   ```bash
   aws ecr create-repository --repository-name athenec-backend
   aws ecr create-repository --repository-name athenec-frontend
   ```

2. **Login y push**:
   ```bash
   AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
   REGION=us-east-1
   aws ecr get-login-password --region $REGION | \
     docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com

   docker build -t athenec-backend ./backend
   docker tag athenec-backend:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/athenec-backend:latest
   docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/athenec-backend:latest

   docker build -t athenec-frontend ./frontend
   docker tag athenec-frontend:latest $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/athenec-frontend:latest
   docker push $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/athenec-frontend:latest
   ```

3. **Crear los servicios App Runner** desde la consola:
   - Backend: origen `ECR` -> imagen `athenec-backend:latest`. Puerto 8000. Variables de entorno: `ADMIN_TOKEN`, `DATABASE_URL` (apuntando a RDS - ver mas abajo), `FRONTEND_ORIGIN`, `SMTP_*`. Health check: `/health`.
   - Frontend: origen `ECR` -> imagen `athenec-frontend:latest`. Puerto 80. Antes de esto, cambia en `nginx.conf` `http://backend:8000/api/` por la URL publica del backend en App Runner.

4. **Base de datos**: reemplaza SQLite por PostgreSQL en RDS:
   - Crea instancia RDS PostgreSQL (t3.micro).
   - En el .env del backend, `DATABASE_URL=postgresql+psycopg2://usuario:pass@host:5432/athenec`.
   - Agrega `psycopg2-binary` a `requirements.txt`.
   - Al primer arranque, `Base.metadata.create_all()` crea las tablas.

5. **Dominio y TLS**: cada servicio App Runner ya viene con HTTPS. Para tu dominio propio, agrega el CNAME en App Runner -> Custom domains.

**Costo estimado:** backend `0.5 vCPU / 1 GB` + frontend `0.25 vCPU / 0.5 GB` + RDS t3.micro = ~USD 40-60/mes.

---

## 3. AWS ECS Fargate + ALB (control fino, produccion seria)

Recomendado si esperas trafico serio o necesitas mas control.

### Componentes

| Recurso | Rol |
|---------|-----|
| **ECR** | Registry de imagenes Docker |
| **ECS Cluster (Fargate)** | Ejecuta contenedores sin gestionar EC2 |
| **Task Definitions** | Una por servicio (backend, frontend) |
| **Application Load Balancer** | Enruta HTTP/HTTPS a los servicios |
| **Target Groups** | Routing por path: `/api/*` -> backend, `/*` -> frontend |
| **RDS PostgreSQL** | Base de datos |
| **Secrets Manager** | Guarda `ADMIN_TOKEN`, `SMTP_PASSWORD`, `DATABASE_URL` |
| **CloudWatch Logs** | Logs de contenedores |
| **Route 53** | DNS |
| **ACM** | Certificado TLS |

### Terraform (esqueleto)

Crea `infra/main.tf`:

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = "us-east-1" }

resource "aws_ecs_cluster" "athenec" { name = "athenec" }

# ... task definitions, ALB, target groups, RDS, security groups, IAM roles ...
```

Un ejemplo completo esta fuera del alcance de este MVP, pero la arquitectura target es:

```
  Internet
    v
 [ALB + TLS]
    |------> /api/*  -> Target Group backend  -> Task ECS backend
    +------> /*      -> Target Group frontend -> Task ECS frontend
                                                     |
                                                     v
                                              [RDS PostgreSQL]
```

---

## Checklist antes de subir a produccion

- [ ] Cambia `ADMIN_TOKEN` a algo largo y aleatorio:
      `python -c "import secrets; print(secrets.token_urlsafe(48))"`
- [ ] Migra de SQLite a PostgreSQL (RDS)
- [ ] Configura SMTP real (Amazon SES, SendGrid, Mailgun)
- [ ] Actualiza `FRONTEND_ORIGIN` con tu dominio productivo
- [ ] En el frontend, cambia las URLs hardcodeadas `http://localhost:8000/api` por tu URL de backend productivo (o usa `/api` si esta detras del mismo dominio via nginx)
- [ ] Habilita HTTPS (App Runner lo trae; ECS + ALB requiere ACM)
- [ ] Configura backups automaticos de RDS
- [ ] Guarda secretos en AWS Secrets Manager o Parameter Store, no en `.env`
- [ ] Configura CloudWatch alarmas: latencia, error rate, CPU, memoria
- [ ] Sube el logo real como archivo estatico o a S3 + CloudFront
- [ ] Ejecuta un pen-test / audit basico antes de anunciar

---

## Costos aproximados

| Opcion | Costo mensual estimado | Complejidad |
|--------|------------------------|-------------|
| Docker Compose local | 0 | Baja |
| App Runner + RDS t3.micro | ~USD 45 | Baja |
| ECS Fargate + ALB + RDS | ~USD 60-120 | Media |
| EC2 t3.small (docker compose) + RDS | ~USD 25-40 | Media |

Para lanzamiento MVP, **App Runner es la opcion recomendada**: HTTPS automatico, escala a cero cuando no hay trafico y no requiere gestionar infraestructura.
