---
name: rotacao-senha-legado-ago2026
description: "App tinha o mesmo padrão de conexão direta (DB_HOST=host-postgres/DB_USER=postgres) do incidente do relatorios — descoberta e corrigida preventivamente numa varredura completa em 05/08/2026, antes de dar erro pro usuário"
metadata:
  node_type: memory
  type: project
  originSessionId: session_01LWwXEKicVtyv8davwHFau9
---

Em 05/08/2026, a senha do superusuário `postgres` do Postgres **nativo** da VPS (banco `sga`, o legado monolítico) foi rotacionada pelo guarda-chuva `multi-aplicacao` (ver `rotacao_credenciais_vps_agosto2026.md` lá para o histórico completo).

`dashboard` conecta direto nesse Postgres — `DB_HOST=host-postgres` (gateway Docker, `172.17.0.1`), `DB_USER=postgres`, `DB_NAME=sga`, `.env` plano via `env_file`. Mesmo padrão exato do incidente real que quebrou o `relatorios` (ver memória equivalente lá) — mas aqui foi encontrado **preventivamente**, numa varredura completa por `DB_USER=postgres` + hosts do banco em todos os `.env` de `/home/deploy/apps/*/`, feita depois do incidente do relatorios. Corrigido: `.env` (`DB_PASSWORD`) atualizado + `docker stack deploy -c stack.yml dashboard`. Validado com `psycopg2.connect()` real dentro do container novo, sem a app nunca ter ficado fora do ar visivelmente para o usuário.

**Why:** apps fora do padrão Django/Swarm-secret são um ponto cego real em rotações de credencial.

**How to apply:** numa próxima rotação da senha do `postgres` legado, sempre incluir este app na lista de consumidores a atualizar (`DB_PASSWORD` no `.env`, seguido de `docker stack deploy`).
