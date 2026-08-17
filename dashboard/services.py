"""
Services do DashBoard — regras de negócio simples que não pertencem a `panels.py`
(camada de renderização) nem a `models.py` (camada de dados).

Adicionado na auditoria de 17/08/2026: as gravações da tela "Gerenciar" (Meta,
Mensagens, Configuração de exibição) não tinham Log Duplo (regra 11 do CLAUDE.md).
`registrar_log` implementa o mesmo padrão já usado em todo o ecossistema oficial —
banco (`Log`, auditoria) + sistema (`admin_logger`, monitoramento).

Limitação conhecida e aceita pelo usuário (achado CRÍTICA da mesma auditoria, decisão
"Deixe como está"): a tela "Gerenciar" não tem autenticação, então não há como saber
*quem* fez a alteração — `NomeUsuario` sempre grava o identificador fixo abaixo,
deixando explícito no próprio log que a app não identifica o autor real.
"""

import logging

from django.utils import timezone

from dashboard.models import Log

admin_logger = logging.getLogger("admin_logger")
erro_logger = logging.getLogger("erro_logger")

USUARIO_SEM_AUTENTICACAO = "Dashboard (sem autenticação)"

# Códigos de ação — mesmo padrão do restante do ecossistema oficial.
ACAO_INCLUSAO = 4
ACAO_ALTERACAO = 3
ACAO_EXCLUSAO = 5


def registrar_log(descricao: str, acao: int = ACAO_ALTERACAO) -> None:
    """Grava o Log Duplo (banco + sistema) de uma alteração feita na tela
    "Gerenciar". Nunca levanta exceção — uma falha ao logar não pode derrubar a
    gravação de negócio que já aconteceu."""
    agora = timezone.localtime()
    try:
        Log.objects.create(
            NomeUsuario=USUARIO_SEM_AUTENTICACAO,
            Acao=acao,
            Descricao=descricao[:200],
            Data=agora.date(),
            Hora=agora.time(),
        )
    except Exception as exc:
        erro_logger.error(f"registrar_log: falha ao gravar em Log (banco) — {exc}")

    admin_logger.info(f"{descricao} - Usuário: {USUARIO_SEM_AUTENTICACAO}")
