# Monitor Dokumentów (mdocs)

MVP do monitorowania dokumentów przekazywanych do biura rachunkowego.

## Zakres

- Logowanie administratora
- Klienci, dokumenty i okresy
- Mapowanie adresu e-mail nadawcy do klienta
- Symulacja wpływu wiadomości (nie jest to integracja IMAP)
- Lista nieznanych nadawców i szkice przypomnień (bez wysyłki)

## Standardowy deployment z PostgreSQL

```bash
cp .env.example .env
# edytuj .env: DB_PASSWORD i SECRET_KEY
docker compose up -d --build
docker compose exec web flask init-db
docker compose exec -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD='choose-a-unique-long-password' web flask create-admin
```

Serwis nasłuchuje na 127.0.0.1:8000. W środowisku produkcyjnym użyj HTTPS przez reverse proxy / Cloudflare Tunnel oraz ustaw COOKIE_SECURE=1.

## Raspberry Pi Zero 2 W (ARM64, SQLite)

Dedykowana instalacja bez PostgreSQL: [docs/RPI_ZERO_2_W.md](docs/RPI_ZERO_2_W.md).

```sh
docker compose -f compose.rpi.yaml up -d
```

Wymaga obrazu z manifestem `linux/arm64`, opublikowanego w GHCR.

## Testy

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Wydania

Po wypchnięciu taga `v*`, GitHub Actions uruchamia testy i publikuje obraz w GHCR. Przed aktualizacją wykonuj backup i sprawdzaj zgodność schematu.

## Ograniczenia

Projekt jest prototypowym MVP, a nie gotowym systemem księgowym. Brak IMAP, OCR, LLM, migracji Alembic, pełnego audytu i izolacji organizacji. Nie używaj rzeczywistych danych klientów bez przeglądu bezpieczeństwa.
