"""
Athenec - Servicio de notificaciones por correo
================================================
Se usa desde FastAPI BackgroundTasks para no bloquear la respuesta.

Comportamiento segun .env:
- Si SMTP_HOST, SMTP_USER y SMTP_PASSWORD estan definidos -> envia correo real.
- Si NO estan definidos -> imprime en consola (modo dev / demo).
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

log = logging.getLogger("athenec.email")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")


def _smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "").strip(),
        "port": int(os.getenv("SMTP_PORT", "587") or 587),
        "user": os.getenv("SMTP_USER", "").strip(),
        "password": os.getenv("SMTP_PASSWORD", "").strip(),
        "to": os.getenv("CONTACT_EMAIL", "contacto@athenec.com").strip(),
        "from_addr": os.getenv("SMTP_USER", "").strip() or "no-reply@athenec.com",
    }


TITULOS = {
    "soluciones": "Nueva cotizacion de software",
    "asesoria": "Nueva solicitud de asesoria de tesis",
    "equipos": "Nueva consulta de equipos",
}


def notificar_nueva_cotizacion(
    *,
    tipo: str,
    ticket_id: str,
    nombre_cliente: str,
    correo: str,
    detalle: str,
) -> None:
    """
    Punto unico de envio. tipo in {soluciones, asesoria, equipos}.
    Nunca lanza excepcion: si falla, solo loguea.
    """
    titulo = TITULOS.get(tipo, "Nueva solicitud")
    subject = f"[Athenec] {titulo} - {ticket_id}"
    body = (
        f"{titulo}\n"
        f"===================================\n\n"
        f"Ticket:  {ticket_id}\n"
        f"Cliente: {nombre_cliente}\n"
        f"Correo:  {correo}\n"
        f"Tipo:    {tipo}\n\n"
        f"Detalle:\n{detalle}\n\n"
        f"---\n"
        f"Athenec - notificacion automatica\n"
    )

    cfg = _smtp_config()

    # Modo demo/dev: no hay SMTP configurado -> log a consola
    if not (cfg["host"] and cfg["user"] and cfg["password"]):
        log.info("=" * 60)
        log.info("[NOTIFICACION DEV - SMTP no configurado]")
        log.info("Para: %s", cfg["to"])
        log.info("Asunto: %s", subject)
        log.info("\n%s", body)
        log.info("=" * 60)
        return

    # Envio real
    try:
        msg = MIMEMultipart()
        msg["From"] = cfg["from_addr"]
        msg["To"] = cfg["to"]
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
            server.starttls()
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["from_addr"], [cfg["to"]], msg.as_string())
        log.info("Notificacion enviada por SMTP a %s (ticket %s)", cfg["to"], ticket_id)
    except Exception as e:
        # No propagamos para no romper el POST
        log.warning("Fallo el envio SMTP para ticket %s: %s", ticket_id, e)
