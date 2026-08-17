"""
Testes automatizados do DashBoard.

Achado de auditoria (17/08/2026): `dashboard/tests.py` era o stub vazio padrão do
`startapp`, zero cobertura. Escopo aqui: as funções puras de `panels.py` (parsing/
formatação/cálculo de período) — não dependem de banco, então rodam com o test
runner padrão do Django sem infraestrutura extra (os demais models são
`managed=False` sobre tabelas do legado `sga`, fora do escopo de teste automatizado
por ora — mesma decisão já tomada em `comex`/`monitor-rpa` para apps que conectam
direto ao legado).

Rodar: `python manage.py test dashboard`
"""

from decimal import Decimal
from unittest.mock import patch

from django.test import SimpleTestCase

from dashboard.panels import (
    format_currency,
    get_filtros_periodo,
    parse_quantidade,
    parse_valor,
)


class ParseValorTest(SimpleTestCase):
    def test_aceita_decimal(self):
        self.assertEqual(parse_valor(Decimal("10.50")), Decimal("10.50"))

    def test_aceita_int_e_float(self):
        self.assertEqual(parse_valor(10), Decimal("10"))
        self.assertEqual(parse_valor(10.5), Decimal("10.5"))

    def test_aceita_string_com_virgula(self):
        self.assertEqual(parse_valor("1234,56"), Decimal("1234.56"))

    def test_aceita_string_com_ponto(self):
        self.assertEqual(parse_valor("1234.56"), Decimal("1234.56"))

    def test_valor_invalido_retorna_zero_sem_lancar_excecao(self):
        # Regressão do achado de auditoria: antes caía num `except:` genérico e
        # silencioso — agora captura exceções específicas, mas o comportamento de
        # fallback para o chamador continua o mesmo (não pode quebrar o dashboard).
        self.assertEqual(parse_valor("não é um número"), Decimal("0"))
        self.assertEqual(parse_valor(None), Decimal("0"))
        self.assertEqual(parse_valor(object()), Decimal("0"))

    @patch("dashboard.panels.erro_logger")
    def test_valor_invalido_loga_o_erro(self, erro_logger_mock):
        # Regressão do achado: o `except:` genérico não deixava rastro nenhum de
        # que algo deu errado — agora precisa logar via erro_logger.
        parse_valor("não é um número")
        erro_logger_mock.error.assert_called_once()


class ParseQuantidadeTest(SimpleTestCase):
    def test_aceita_valores_validos(self):
        self.assertEqual(parse_quantidade(5), Decimal("5"))
        self.assertEqual(parse_quantidade("5,5"), Decimal("5.5"))

    def test_valor_invalido_retorna_zero_sem_lancar_excecao(self):
        self.assertEqual(parse_quantidade("abc"), Decimal("0"))

    @patch("dashboard.panels.erro_logger")
    def test_valor_invalido_loga_o_erro(self, erro_logger_mock):
        parse_quantidade("abc")
        erro_logger_mock.error.assert_called_once()


class FormatCurrencyTest(SimpleTestCase):
    def test_formata_padrao_brasileiro(self):
        self.assertEqual(format_currency(1234.5), "R$ 1.234,50")

    def test_formata_zero(self):
        self.assertEqual(format_currency(0), "R$ 0,00")


class GetFiltrosPeriodoTest(SimpleTestCase):
    def test_retorna_primeiro_dia_do_mes_e_hoje(self):
        # Regressão do achado de auditoria: usava `datetime.now()` (naive) em vez de
        # `timezone.localdate()` — aqui só confirma o formato/coerência do retorno,
        # não depende de horário do sistema.
        data_inicial, data_final = get_filtros_periodo()
        self.assertRegex(data_inicial, r"^01/\d{2}/\d{4}$")
        self.assertRegex(data_final, r"^\d{2}/\d{2}/\d{4}$")
        # Mês/ano do início e do fim precisam bater (mesmo período corrente).
        self.assertEqual(data_inicial[3:], data_final[3:])


class RegistrarLogTest(SimpleTestCase):
    """`dashboard/services.py::registrar_log` — Log Duplo adicionado na auditoria
    de 17/08/2026 para as gravações da tela "Gerenciar", que não tinham nenhum
    rastro de auditoria."""

    @patch("dashboard.services.Log.objects.create")
    @patch("dashboard.services.admin_logger")
    def test_registra_log_de_banco_e_de_sistema(
        self, admin_logger_mock, log_create_mock
    ):
        from dashboard.services import registrar_log

        registrar_log("Dashboard [Gerenciar] - Meta de Vendas alterada")

        log_create_mock.assert_called_once()
        admin_logger_mock.info.assert_called_once()

    @patch(
        "dashboard.services.Log.objects.create", side_effect=Exception("sem conexão")
    )
    @patch("dashboard.services.erro_logger")
    @patch("dashboard.services.admin_logger")
    def test_falha_no_log_de_banco_nao_impede_o_log_de_sistema(
        self, admin_logger_mock, erro_logger_mock, log_create_mock
    ):
        # A gravação de negócio (o `.save()` real) já aconteceu antes de chamar
        # `registrar_log` — uma falha ao logar nunca pode propagar e mascarar que a
        # ação principal teve sucesso.
        from dashboard.services import registrar_log

        registrar_log("Dashboard [Gerenciar] - Meta de Vendas alterada")

        erro_logger_mock.error.assert_called_once()
        admin_logger_mock.info.assert_called_once()
