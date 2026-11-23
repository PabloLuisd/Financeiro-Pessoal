# Initial schema, kept as the original schema so existing local installations
# can apply 0002 and remove bank-account registration safely.
import decimal
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
                ('tipo', models.CharField(choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')], max_length=10)),
                ('cor', models.CharField(default='#64748b', max_length=7)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categorias', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Categoria', 'verbose_name_plural': 'Categorias', 'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='Conta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
                ('tipo', models.CharField(choices=[('CORRENTE', 'Conta corrente'), ('POUPANCA', 'Poupança'), ('DINHEIRO', 'Dinheiro'), ('CARTAO', 'Cartão')], default='CORRENTE', max_length=12)),
                ('saldo_inicial', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0'))])),
                ('ativa', models.BooleanField(default=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contas', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['nome']},
        ),
        migrations.CreateModel(
            name='MetaFinanceira',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=120)),
                ('descricao', models.TextField(blank=True)),
                ('valor_objetivo', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))])),
                ('valor_atual', models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0'))])),
                ('prazo', models.DateField(blank=True, null=True)),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metas', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['prazo', 'titulo']},
        ),
        migrations.CreateModel(
            name='Transacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')], max_length=10)),
                ('descricao', models.CharField(max_length=150)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))])),
                ('data', models.DateField(default=django.utils.timezone.localdate)),
                ('observacao', models.TextField(blank=True)),
                ('parcelas', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('parcela_atual', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transacoes', to='financas.categoria')),
                ('conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transacoes', to='financas.conta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacoes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-data', '-criado_em']},
        ),
        migrations.AddConstraint(
            model_name='categoria',
            constraint=models.UniqueConstraint(fields=('usuario', 'nome', 'tipo'), name='categoria_unica_por_usuario_tipo'),
        ),
        migrations.AddConstraint(
            model_name='conta',
            constraint=models.UniqueConstraint(fields=('usuario', 'nome'), name='conta_unica_por_usuario'),
        ),
    ]
