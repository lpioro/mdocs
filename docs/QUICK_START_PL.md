# Monitor Dokumentów — szybka dokumentacja

**Wersja docelowa:** 0.2.0 ARM64 · Raspberry Pi Zero 2 W · Flask + SQLite + Docker

## Opis
Monitor Dokumentów (mdocs) to demonstracyjna aplikacja webowa do ewidencji dokumentów przekazywanych przez klientów biura rachunkowego. MVP oferuje:
- logowanie administratora;
- rejestr klientów i dokumentów z okresem rozliczeniowym;
- mapowanie adresów e-mail nadawców na klientów;
- symulację odebrania wiadomości i oznaczenie nieznanych nadawców;
- przygotowanie szkiców przypomnień (bez wysyłki).

Nie ma jeszcze pobierania wiadomości IMAP, OCR, AI ani automatycznego wysyłania przypomnień.

## Architektura
Przeglądarka → Bootstrap 5 → Flask/Gunicorn (jeden worker) → SQLite (trwały wolumen Dockera).

## Instalacja na Raspberry Pi Zero 2 W
Wymagane: Raspberry Pi OS Lite 64-bit, Docker Engine, Docker Compose oraz **opublikowany** obraz `ghcr.io/lpioro/mdocs:arm64-0.2.0`.

Sprawdź architekturę:
```sh
uname -m
# aarch64
```

Pobierz konfigurację (po opublikowaniu taga `v0.2.0`):
```sh
mkdir -p ~/mdocs && cd ~/mdocs
curl -fsSLo compose.rpi.yaml https://raw.githubusercontent.com/lpioro/mdocs/v0.2.0/compose.rpi.yaml
curl -fsSLo .env.example https://raw.githubusercontent.com/lpioro/mdocs/v0.2.0/.env.example
cp .env.example .env
nano .env
```

W pliku `.env` ustaw własny `SECRET_KEY`. Wygenerujesz go np.:
```sh
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Uruchom:
```sh
docker compose -f compose.rpi.yaml pull
docker compose -f compose.rpi.yaml up -d
docker compose -f compose.rpi.yaml exec web flask init-db
```

Utwórz konto administratora (użyj **własnego** silnego hasła):
```sh
docker compose -f compose.rpi.yaml exec -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD='ZMIEN_NA_DLUGIE_HASLO' web flask create-admin
```

## Dostęp
Aplikacja nasłuchuje tylko na `127.0.0.1:8000` Raspberry Pi. Dostęp z innych urządzeń wymaga np. reverse proxy lub Cloudflare Tunnel z HTTPS. Przy HTTPS ustaw `COOKIE_SECURE=1` w `.env` i uruchom kontener ponownie.

## Administracja
W katalogu `~/mdocs`:
```sh
docker compose -f compose.rpi.yaml ps
docker compose -f compose.rpi.yaml logs --tail=100 web
docker compose -f compose.rpi.yaml restart
docker compose -f compose.rpi.yaml down
```

Nie używaj `down -v`, bo usuwa dane wolumenu. Aktualizację poprzedzaj kopią bazy SQLite; sam `flask init-db` **nie jest** migracją schematu.

## Linki
- [Repozytorium](https://github.com/lpioro/mdocs)
- [Pełna dokumentacja Raspberry Pi](RPI_ZERO_2_W.md)
- [GitHub Actions](https://github.com/lpioro/mdocs/actions)
- [Wydania](https://github.com/lpioro/mdocs/releases)

> To MVP do testów. Nie przetwarzaj prawdziwych danych klientów bez oceny bezpieczeństwa, kopii zapasowych i odpowiednich procedur ochrony danych.
