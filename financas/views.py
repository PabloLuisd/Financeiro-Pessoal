from datetime import date
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import CadastroForm, TransacaoForm, CategoriaForm, MetaFinanceiraForm
from .models import Transacao, Categoria, MetaFinanceira



CATEGORIAS_PADRAO = {
    'RECEITA': [
        ('Salário', '#16a34a'), ('Freelance', '#22c55e'),
        ('Investimentos', '#0d9488'), ('Vendas', '#14b8a6'),
        ('Renda extra', '#65a30d'), ('Reembolso', '#84cc16'),
        ('Outras receitas', '#64748b'),
    ],
    'DESPESA': [
        ('Moradia', '#2563eb'), ('Alimentação', '#f97316'),
        ('Transporte', '#0ea5e9'), ('Saúde', '#ef4444'),
        ('Educação', '#8b5cf6'), ('Lazer', '#d946ef'),
        ('Compras', '#ec4899'), ('Contas e serviços', '#64748b'),
        ('Assinaturas', '#6366f1'), ('Impostos e taxas', '#a16207'),
        ('Cuidados pessoais', '#db2777'), ('Pets', '#a855f7'),
        ('Viagens', '#0891b2'), ('Presentes e doações', '#e11d48'),
        ('Outras despesas', '#475569'),
    ],
}

def garantir_categorias_padrao(usuario):
    for tipo, categorias in CATEGORIAS_PADRAO.items():
        for nome, cor in categorias:
            Categoria.objects.get_or_create(
                usuario=usuario, nome=nome, tipo=tipo,
                defaults={'cor': cor},
            )

def inicio(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = CadastroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save()
        login(request, usuario)
        messages.success(request, 'Conta de acesso criada. Bem-vindo ao seu controle financeiro!')
        return redirect('dashboard')
    return render(request, 'financas/cadastro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    erro = None
    if request.method == 'POST':
        email_ou_usuario = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')
        usuario = authenticate(request, username=email_ou_usuario, password=senha)
        if usuario is None:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            encontrado = User.objects.filter(email__iexact=email_ou_usuario).first()
            if encontrado:
                usuario = authenticate(request, username=encontrado.username, password=senha)
        if usuario:
            login(request, usuario)
            return redirect(request.GET.get('next') or 'dashboard')
        erro = 'E-mail/usuário ou senha inválidos.'
    return render(request, 'financas/login.html', {'erro': erro})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


@login_required
def dashboard(request):
    garantir_categorias_padrao(request.user)
    hoje = timezone.localdate()
    transacoes = Transacao.objects.filter(usuario=request.user)
    mes = transacoes.filter(data__year=hoje.year, data__month=hoje.month)
    receitas_mes = mes.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    despesas_mes = mes.filter(tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    receitas_total = transacoes.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    despesas_total = transacoes.filter(tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
    saldo_total = receitas_total - despesas_total
    ultimas = transacoes.select_related('categoria')[:7]
    despesas_categoria = mes.filter(tipo='DESPESA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')[:5]
    total_despesas_categoria = sum((item['total'] for item in despesas_categoria), Decimal('0'))
    for item in despesas_categoria:
        item['percentual'] = int(item['total'] / total_despesas_categoria * 100) if total_despesas_categoria else 0
    return render(request, 'financas/dashboard.html', {
        'hoje': hoje, 'receitas_mes': receitas_mes, 'despesas_mes': despesas_mes,
        'resultado_mes': receitas_mes - despesas_mes, 'receitas_total': receitas_total,
        'despesas_total': despesas_total, 'saldo_total': saldo_total,
        'ultimas': ultimas, 'despesas_categoria': despesas_categoria,
    })


@login_required
def transacao_lista(request):
    transacoes = Transacao.objects.filter(usuario=request.user).select_related('categoria')
    tipo = request.GET.get('tipo')
    if tipo in ('RECEITA', 'DESPESA'):
        transacoes = transacoes.filter(tipo=tipo)
    busca = request.GET.get('busca', '').strip()
    if busca:
        transacoes = transacoes.filter(descricao__icontains=busca)
    return render(request, 'financas/transacoes.html', {'transacoes': transacoes, 'tipo_selecionado': tipo or '', 'busca': busca})


@login_required
def transacao_criar(request):
    garantir_categorias_padrao(request.user)
    form = TransacaoForm(request.POST or None, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        transacao = form.save(commit=False)
        transacao.usuario = request.user
        transacao.save()
        messages.success(request, 'Transação cadastrada com sucesso.')
        return redirect('transacao_lista')
    return render(request, 'financas/formulario.html', {'form': form, 'titulo': 'Nova transação'})


@login_required
def transacao_editar(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    form = TransacaoForm(request.POST or None, instance=transacao, usuario=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Transação atualizada.')
        return redirect('transacao_lista')
    return render(request, 'financas/formulario.html', {'form': form, 'titulo': 'Editar transação'})


@login_required
def transacao_excluir(request, pk):
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)
    if request.method == 'POST':
        transacao.delete()
        messages.success(request, 'Transação excluída.')
        return redirect('transacao_lista')
    return render(request, 'financas/confirmar_exclusao.html', {'objeto': transacao, 'voltar': 'transacao_lista'})


@login_required
def categoria_lista(request):
    garantir_categorias_padrao(request.user)
    categorias = Categoria.objects.filter(usuario=request.user)
    return render(request, 'financas/categorias.html', {'categorias': categorias})


@login_required
def categoria_criar(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        categoria = form.save(commit=False)
        categoria.usuario = request.user
        try:
            categoria.save()
            messages.success(request, 'Categoria criada.')
            return redirect('categoria_lista')
        except Exception:
            form.add_error('nome', 'Você já possui uma categoria com esse nome e tipo.')
    return render(request, 'financas/formulario.html', {'form': form, 'titulo': 'Nova categoria'})


@login_required
def meta_lista(request):
    metas = MetaFinanceira.objects.filter(usuario=request.user)
    return render(request, 'financas/metas.html', {'metas': metas})


@login_required
def meta_criar(request):
    form = MetaFinanceiraForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        meta = form.save(commit=False)
        meta.usuario = request.user
        meta.save()
        messages.success(request, 'Meta criada.')
        return redirect('meta_lista')
    return render(request, 'financas/formulario.html', {'form': form, 'titulo': 'Nova meta financeira'})


@login_required
def meta_editar(request, pk):
    meta = get_object_or_404(MetaFinanceira, pk=pk, usuario=request.user)
    form = MetaFinanceiraForm(request.POST or None, instance=meta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Meta atualizada.')
        return redirect('meta_lista')
    return render(request, 'financas/formulario.html', {'form': form, 'titulo': 'Editar meta'})


@login_required
def relatorios(request):
    ano_atual = timezone.localdate().year
    try:
        ano = int(request.GET.get('ano', ano_atual))
        if ano < 2000 or ano > 2100:
            ano = ano_atual
    except (TypeError, ValueError):
        ano = ano_atual
    qs = Transacao.objects.filter(usuario=request.user, data__year=ano)
    meses = []
    for numero in range(1, 13):
        dados = qs.filter(data__month=numero)
        receita = dados.filter(tipo='RECEITA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        despesa = dados.filter(tipo='DESPESA').aggregate(total=Sum('valor'))['total'] or Decimal('0')
        meses.append({'nome': date(ano, numero, 1).strftime('%b').capitalize(), 'receita': receita, 'despesa': despesa, 'saldo': receita - despesa})
    maior = max([max(m['receita'], m['despesa']) for m in meses] + [Decimal('1')])
    for mes in meses:
        mes['receita_pct'] = int(mes['receita'] / maior * 100)
        mes['despesa_pct'] = int(mes['despesa'] / maior * 100)
    return render(request, 'financas/relatorios.html', {'meses': meses, 'ano': ano, 'anos': range(ano_atual - 4, ano_atual + 1)})
