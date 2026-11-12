import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from app.models import Familia, MovimentacaoEstoque, Retirada
from app.services import registrar_retirada


class Command(BaseCommand):
    help = "Cria dados fictícios de demonstração (somente se DEMO_SEED=1)."

    def handle(self, *args, **options):
        if os.environ.get("DEMO_SEED") != "1":
            self.stdout.write("DEMO_SEED não ativo; nada a fazer.")
            return
        senha = os.environ.get("DEMO_PASSWORD")
        if not senha:
            self.stdout.write("Defina DEMO_PASSWORD.")
            return
        User = get_user_model()
        coord, criado = User.objects.get_or_create(
            username="coordenacao.demo", defaults={"is_staff": True}
        )
        if criado:
            coord.set_password(senha)
            coord.save()
        vol, criado = User.objects.get_or_create(username="voluntario.demo")
        if criado:
            vol.set_password(senha)
            vol.save()
        for nome, doc, n in [
            ("Ana Exemplo", "1001", 4),
            ("Marta Teste", "1002", 3),
            ("Paulo Demonstração", "1003", 5),
        ]:
            Familia.objects.get_or_create(
                documento=doc, defaults={"nome_responsavel": nome, "qtd_pessoas": n}
            )
        if not MovimentacaoEstoque.objects.exists():
            MovimentacaoEstoque.objects.create(
                tipo=MovimentacaoEstoque.ENTRADA, quantidade=14, usuario=coord
            )
        if not Retirada.objects.exists():
            registrar_retirada(Familia.objects.get(documento="1002").id, coord)
        self.stdout.write("Dados de demonstração prontos.")
