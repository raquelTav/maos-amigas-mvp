from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint


class Familia(models.Model):
    nome_responsavel = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    qtd_pessoas = models.PositiveIntegerField(default=1)
    ativa = models.BooleanField(default=True)
    data_cadastro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nome_responsavel


class Retirada(models.Model):
    familia = models.ForeignKey(Familia, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_retirada = models.DateTimeField(auto_now_add=True)
    mes_referencia = models.DateField()
    ativa = models.BooleanField(default=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["familia", "mes_referencia"],
                condition=Q(ativa=True),
                name="uma_retirada_ativa_por_familia_por_mes",
            )
        ]


class MovimentacaoEstoque(models.Model):
    ENTRADA = "entrada"
    SAIDA = "saida"
    TIPOS = [(ENTRADA, "Entrada"), (SAIDA, "Saída")]

    item = models.CharField(max_length=80, default="Cesta básica")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.PositiveIntegerField()
    data_movimento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    retirada = models.OneToOneField(
        Retirada, null=True, blank=True, on_delete=models.PROTECT
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gt=0), name="quantidade_positiva"
            )
        ]
