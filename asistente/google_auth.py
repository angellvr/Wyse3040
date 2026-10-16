"""Autoriza el acceso a Google Drive y guarda el token en data/google_token.json.

Ejecútalo UNA vez en un ordenador con navegador:
    python -m asistente.google_auth
y copia data/google_token.json al Wyse (scp). El token se renueva solo.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

from .config import cargar
from .modules.drive import SCOPES


def main() -> None:
    cfg = cargar()
    flujo = InstalledAppFlow.from_client_secrets_file(str(cfg.google_cliente), SCOPES)
    creds = flujo.run_local_server(port=0)
    cfg.google_token.write_text(creds.to_json(), encoding="utf-8")
    print(f"Token guardado en {cfg.google_token}")


if __name__ == "__main__":
    main()
