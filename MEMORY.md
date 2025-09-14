# MEMORY.md — Mémoire messages (SQLite en dev / Postgres en prod)

But (1 page, pragmatique)
- Stocker l’historique (IN/OUT) pour améliorer le prompt et tracer les incidents.
- Dev : SQLite (`local.db`) automatique. Prod : Postgres (Render), via `DATABASE_URL`.
- Ceci est **de la documentation** : les blocs SQL ci-dessous peuvent être exécutés dans DBeaver/psql **optionnellement**.
  L’app crée le schéma au démarrage via `init_schema()`.
- Ne jamais mettre de secrets ici ; utilisez `.env` local / ENV Render.

## 1) Connexions

### Local (SQLite)
- Fichier : `./local.db` (créé par `init_schema()` au boot).
- DBeaver : Database → New → **SQLite** → File → pointer sur `local.db`.

### Prod (Postgres Render)
- Variable : `DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db>`
- Render → Dashboard → (PostgreSQL add-on) → External Connection → copier **host/port/db/user/password**.
- DBeaver : New → **PostgreSQL** → Host/Port/DB/User/Password → SSL **Require** → Test Connection.

> Rappel sécurité : secrets uniquement dans ENV Render / `.env` local.

## 2) Schéma SQL (documentation + exécutable dans DBeaver si besoin)

### SQLite (dev)
```sql
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_phone TEXT NOT NULL,
  direction TEXT CHECK (direction IN ('IN','OUT')) NOT NULL,
  text TEXT,
  msg_sid TEXT,
  source TEXT DEFAULT 'whatsapp',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_messages_sid_dir ON messages(msg_sid, direction);
CREATE INDEX IF NOT EXISTS ix_messages_user_created ON messages(user_phone, created_at);
