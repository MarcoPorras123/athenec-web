"""
Athenec - Autenticacion del panel admin
========================================
Esquema simple para MVP: token compartido en .env (ADMIN_TOKEN),
enviado por el cliente en el header Authorization: Bearer <token>.

Para produccion, migrar a JWT con usuarios individuales.
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Token unico para MVP. Si no esta seteado, cualquier request es rechazada
# excepto los endpoints publicos (POSTs de formularios y /health).
def _admin_token() -> str:
    return os.getenv("ADMIN_TOKEN", "").strip()


# scheme opcional -> permite responder 401 personalizado en vez de 403
security = HTTPBearer(auto_error=False)


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    """Dependency que exige un Bearer token igual al ADMIN_TOKEN del .env."""
    expected = _admin_token()
    if not expected:
        # Sin token configurado, el panel admin queda inaccesible.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin token no configurado en el servidor.",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta Authorization: Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # ok
