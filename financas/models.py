from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    TIPOS = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categorias')
    nome = models.CharField(max_length=80)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cor = models.CharField(max_length=7, default='#64748b')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        constraints = [models.UniqueConstraint(fields=['usuario', 'nome', 'tipo'], name='categoria_unica_por_usuario_tipo')]

    def __str__(self):
        return f'{self.nome} ({self.get_tipo_display()})'

class Transacao(models.Model):
    TIPOS = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    descricao = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='transacoes')
    data = models.DateField(default=timezone.localdate)
    observacao = models.TextField(blank=True)
    parcelas = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    parcela_atual = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.categoria_id and self.tipo and self.categoria.tipo != self.tipo:
            raise ValidationError({'categoria': 'A categoria precisa ser do mesmo tipo da transação.'})
        if self.parcela_atual > self.parcelas:
            raise ValidationError({'parcela_atual': 'A parcela atual não pode ser maior que o total de parcelas.'})
        if self.categoria_id and self.usuario_id and self.categoria.usuario_id != self.usuario_id:
            raise ValidationError({'categoria': 'Selecione uma categoria pertencente ao seu usuário.'})

    def __str__(self):
        return self.descricao

class MetaFinanceira(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metas')
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    valor_objetivo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    prazo = models.DateField(null=True, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['prazo', 'titulo']

    def __str__(self):
        return self.titulo

    @property
    def percentual(self):
        if not self.valor_objetivo:
            return 0
        return min(100, int((self.valor_atual / self.valor_objetivo) * 100))
