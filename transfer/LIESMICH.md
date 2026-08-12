# SafeWord – Offline-Bundle für Homeserver (Portainer)

Alle Dateien in diesem Ordner sind fertig gebaut – es wird NICHTS vom
Homeserver heruntergeladen. Kein Root noetig (solange der Docker-Socket
fuer deinen Benutzer/Portainer erreichbar ist).

## 1. Dateien uebertragen

Den kompletten Ordner `transfer/` (ca. 236 MB) auf den Homeserver bringen
(z. B. SCP, USB-Stick, Syncthing):

| Datei                             | Inhalt                     |
|-----------------------------------|----------------------------|
| `safeword-api.tar.gz`             | Fertiges API-Image         |
| `safewordbot.tar.gz`              | Fertiges Bot-Image         |
| `postgres-16-alpine.tar.gz`       | PostgreSQL-Image           |
| `docker-compose.homeserver.yml`   | Compose-File (ohne build)  |
| `docker-compose.yml`              | Compose-File mit build     |
| `.env.example`                    | Vorlage fuer `.env`        |

## 2. Images laden

**Variante A – SSH / docker-CLI (am einfachsten):**
```bash
docker load -i safeword-api.tar.gz
docker load -i safewordbot.tar.gz
docker load -i postgres-16-alpine.tar.gz
```

**Variante B – Portainer-UI:**
`Images` → `Import` → Tar-Archive nacheinander hochladen.

Pruefen mit:
```bash
docker images
# safeword-api:latest  /  safewordbot:latest  /  postgres:16-alpine  muessen erscheinen
```

## 3. `.env` anlegen

Kopie von `.env.example` erstellen und mit deinen Werten fuellen:
```bash
cp .env.example .env
nano .env   # DISCORD_TOKEN, CLIENT_ID, CLIENT_SECRET, JWT_SECRET, ...
```
Fuer das Vercel-Dashboard unbedingt setzen:
```
DISCORD_REDIRECT_URI=https://dashboard-o5wh905cm-dev-coder.vercel.app/api/auth/callback
DASHBOARD_URL=https://dashboard-o5wh905cm-dev-coder.vercel.app
COOKIE_SECURE=true
CORS_ORIGINS=https://dashboard-o5wh905cm-dev-coder.vercel.app
```

## 4. Stack in Portainer deployen

1. `Stacks` → `+ Add stack` → **Web editor**
2. Name: `safeword`
3. Inhalt von `docker-compose.homeserver.yml` einfuegen
4. Wichtig: Die Datei `.env` muss im Stack-Verzeichnis liegen
   (Portainer: Stacks → `safeword` → File-Editor → `.env` anlegen,
   oder per SSH in den Stack-Ordner kopieren).
5. `Deploy the stack`

Falls Portainer Probleme mit `env_file` macht: alle Werte aus der `.env`
direkt als `environment:`-Eintraege in die Compose uebernehmen.

## 5. Fertig

```bash
docker compose -f docker-compose.homeserver.yml ps
# safeword-db / safeword-api / safewordbot  alle Up
```
API-Test: `curl http://<homeserver-ip>:8000/api/health`
