from datetime import date
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Familia, MovimentacaoEstoque, Retirada
from .services import (
    RegraDeNegocioError,
    normalizar_documento,
    registrar_retirada,
    saldo_estoque,
)

LIMITE_ALERTA = 15


@login_required
def menu(request):
    return render(
        request,
        "app/menu.html",
        {"eh_coordenacao": request.user.is_staff},
    )


@login_required
def retirada(request):
    termo = request.GET.get("q", "").strip()
    familias = []

    if termo:
        filtro = Q(nome_responsavel__icontains=termo)
        doc = normalizar_documento(termo)

        if doc:
            filtro |= Q(documento__icontains=doc)

        familias = list(
            Familia.objects.filter(filtro, ativa=True)
            .order_by("nome_responsavel")[:20]
        )

        mes = date.today().replace(day=1)
        ja = set(
            Retirada.objects.filter(
                mes_referencia=mes,
                ativa=True,
            ).values_list("familia_id", flat=True)
        )

        for familia in familias:
            familia.ja_retirou = familia.id in ja

    return render(
        request,
        "app/retirada.html",
        {"termo": termo, "familias": familias},
    )


@login_required
@require_POST
def registrar(request, familia_id):
    try:
        r = registrar_retirada(familia_id, request.user)
        messages.success(
            request,
            f"Retirada registrada para {r.familia.nome_responsavel}.",
        )
    except RegraDeNegocioError as erro:
        messages.error(request, str(erro))

    q = request.POST.get("q", "")
    return redirect(f"{reverse('retirada')}?{urlencode({'q': q})}")


@login_required
def estoque(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Acesso restrito à coordenação.")

    if request.method == "POST":
        try:
            qtd = int(request.POST.get("quantidade", ""))
        except ValueError:
            qtd = 0

        if qtd < 1:
            messages.error(
                request,
                "Informe uma quantidade maior que zero.",
            )
        else:
            MovimentacaoEstoque.objects.create(
                tipo=MovimentacaoEstoque.ENTRADA,
                quantidade=qtd,
                usuario=request.user,
            )
            messages.success(request, "Entrada registrada.")

        return redirect("estoque")

    contexto = {
        "saldo": saldo_estoque(),
        "limite": LIMITE_ALERTA,
        "movs": MovimentacaoEstoque.objects.order_by(
            "-data_movimento"
        )[:5],
    }

    return render(request, "app/estoque.html", contexto)


from django.db import connection
from django.http import HttpResponse


def saude(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return HttpResponse("ok", content_type="text/plain")
    except Exception:
        return HttpResponse("erro", status=503, content_type="text/plain")
