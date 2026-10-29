# Monitor Dokumentów (mdocs)

MVP do monitorowania dokumentów przekazywanych do biura rachunkowego.

## Zakres
- logowanie administratora
- klienci, dokumenty i okresy
- mapowanie adresu e-mail nadawcy do klienta
- symulacja wpływu wiadomości (nie jest to integracja IMAP)
- lista nieznanych nadawców i szkice przypomnień (bez wysyłki)

## Uruchomienie
Wymagany Docker z Docker Compose:

```bash
cp .env.example .env
# edytuj .env i ustaw losowe wartości DB_PASSWORD i SECRET_KEY
docker compose up -d --build
docker compose exec web flask init-db
docker compose exec -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD='ustaw-bezpieczne-haslo-123' web flask create-admin
```

Aplikacja nasłuchuje na 127.0.0.1:8000. W środowisku produkcyjnym ustaw HTTPS przez reverse proxy lub Cloudflare Tunnel oraz COOKIE_SECURE=1.

## Testy
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Aktualizacje
Wersję aplikacji oznacz tagiem v0.1.0: GitHub Actions uruchomi testy i opublikuje obraz w GHCR. Przed aktualizacją wykonaj backup wolumenu PostgreSQL i zadbaj o migrację schematu danych.

## Uwaga
Jest to MVP, nie gotowy produkt księgowy. Nie ma jeszcze IMAP, OCR, LLM, migracji Alembic ani kompletnej izolacji organizacji. Nie używaj prawdziwych danych osobowych klientów bez audytu bezpieczeństwa i procedur RODO.
