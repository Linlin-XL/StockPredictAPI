from django.db import migrations
from django.core.management import call_command


def clear_predictor_table(apps, schema_editor):
    pred_model = apps.get_model('api', 'StockPredictorModel')
    pred_model.objects.all().delete()


def populate_predictor_table(apps, schema_editor):
    clear_predictor_table(apps, schema_editor)
    call_command('loaddata', 'stock_predictor_data.json')


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial')
    ]

    operations = [
        migrations.RunPython(populate_predictor_table, clear_predictor_table)
    ]
