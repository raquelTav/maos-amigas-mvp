from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase

from .models import Familia, MovimentacaoEstoque, Retirada
from .services import (
    RegraDeNegocioError,
    normalizar_documento,
    registrar_retirada,
    saldo_estoque,
)


class NormalizarDocumentoTests(SimpleTestCase):
    """Testes unitários: função isolada, sem banco de dados."""

    def test_remove_pontuacao(self):
        self.assertEqual(normalizar_documento("123.456.789-00"), "12345678900")

    def test_aceita_valor_vazio(self):
        self.assertEqual(normalizar_documento(None), "")

    def test_remove_letras(self):
        self.assertEqual(normalizar_documento("abc"), "")


class EstoqueERetiradaTests(TestCase):
    """Testes de integração: regras de negócio com o banco de dados."""

    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="voluntario.teste", password="senha-so-de-teste"
        )
        self.familia = Familia.objects.create(
            nome_responsavel="Ana Exemplo", documento="1001", qtd_pessoas=4
        )

    def _movimentar(self, tipo, quantidade):
        MovimentacaoEstoque.objects.create(
            tipo=tipo, quantidade=quantidade, usuario=self.usuario
        )

    def test_saldo_inicial_e_zero(self):
        self.assertEqual(saldo_estoque(), 0)

    def test_saldo_e_entradas_menos_saidas(self):
        self._movimentar(MovimentacaoEstoque.ENTRADA, 10)
        self._movimentar(MovimentacaoEstoque.SAIDA, 3)
        self.assertEqual(saldo_estoque(), 7)

    def test_retirada_reduz_saldo_e_registra_saida(self):
        self._movimentar(MovimentacaoEstoque.ENTRADA, 5)
        retirada = registrar_retirada(self.familia.id, self.usuario)
        self.assertEqual(saldo_estoque(), 4)
        saida = MovimentacaoEstoque.objects.get(retirada=retirada)
        self.assertEqual(saida.tipo, MovimentacaoEstoque.SAIDA)

    def test_recusa_segunda_retirada_no_mes(self):
        self._movimentar(MovimentacaoEstoque.ENTRADA, 5)
        registrar_retirada(self.familia.id, self.usuario)
        with self.assertRaises(RegraDeNegocioError):
            registrar_retirada(self.familia.id, self.usuario)
        self.assertEqual(saldo_estoque(), 4)
        self.assertEqual(Retirada.objects.count(), 1)

    def test_recusa_retirada_sem_estoque(self):
        with self.assertRaises(RegraDeNegocioError):
            registrar_retirada(self.familia.id, self.usuario)
        self.assertEqual(Retirada.objects.count(), 0)

    def test_recusa_familia_inativa(self):
        self._movimentar(MovimentacaoEstoque.ENTRADA, 5)
        self.familia.ativa = False
        self.familia.save()
        with self.assertRaises(RegraDeNegocioError):
            registrar_retirada(self.familia.id, self.usuario)

    def test_recusa_familia_inexistente(self):
        with self.assertRaises(RegraDeNegocioError):
            registrar_retirada(9999, self.usuario)

    def test_banco_recusa_documento_duplicado(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Familia.objects.create(
                    nome_responsavel="Outra Pessoa", documento="1001"
                )

    def test_banco_recusa_quantidade_zero(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._movimentar(MovimentacaoEstoque.ENTRADA, 0)