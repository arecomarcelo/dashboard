#!/bin/sh
set -e

# migrate só do app `dashboard` (tabelas próprias no schema `dashboard` do
# oficial_db); os demais models são espelhos managed=False. Réplica única, sem
# advisory lock. Sem collectstatic: o Django admin não é servido via HTTP neste
# deploy — Django roda só em processo, para ORM. Depois o Streamlit sobe.
python manage.py migrate dashboard --noinput

exec "$@"
