import re
from datetime import date

from django.db import transaction
from django.db.models import Sum

from .models import Familia, MovimentacaoEstoque, Retirada


class RegraDeNegocioError(Exception):
    """Erro de regra com mensagem segura para mostrar ao usuário."""


def normalizar_documento(texto):
    return re.sub(r"\D", "", texto or "")


def saldo_estoque(item="Cesta básica"):
    movs = MovimentacaoEstoque.objects.filter(item=item)
    entradas = (
        movs.filter(tipo=MovimentacaoEstoque.ENTRADA).aggregate(t=Sum("quantidade"))["t"] or 0
    )
    saidas = (
        movs.filter(tipo=MovimentacaoEstoque.SAIDA).aggregate(t=Sum("quantidade"))["t"] or 0
    )
    return entradas - saidas


@transaction.atomic
def registrar_retirada(familia_id, usuario):
    try:
        familia = Familia.objects.select_for_update().get(pk=familia_id, ativa=True)
    except Familia.DoesNotExist:
        raise RegraDeNegocioError("Família não encontrada ou inativa.")

    mes = date.today().replace(day=1)
    if Retirada.objects.filter(familia=familia, mes_referencia=mes, ativa=True).exists():
        raise RegraDeNegocioError("Esta família já retirou a cesta deste mês.")
    if saldo_estoque() < 1:
        raise RegraDeNegocioError("Sem cestas no estoque. Avise a coordenação.")

    retirada = Retirada.objects.create(
        familia=familia, usuario=usuario, mes_referencia=mes
    )
    MovimentacaoEstoque.objects.create(
        tipo=MovimentacaoEstoque.SAIDA,
        quantidade=1,
        usuario=usuario,
        retirada=retirada,
    )
    return retirada
