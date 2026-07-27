#!/bin/sh
set -e

# Sem migrate/collectstatic aqui: todos os modelos do DashBoard são managed=False
# (tabelas já existem no banco `sga`) e o Django admin não é servido via HTTP
# neste deploy — Django roda só em processo, para ORM. O Streamlit sobe direto.

exec "$@"
