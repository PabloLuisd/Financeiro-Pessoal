from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('financas', '0001_initial')]

    operations = [
        migrations.RemoveField(model_name='transacao', name='conta'),
        migrations.DeleteModel(name='Conta'),
    ]
