# Generated by Django 3.1.1 on 2022-05-19 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grid_iron', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gridiron',
            name='team_event',
            field=models.CharField(choices=[('PCCOPEN', 'PCCOPEN'), ('PRODSS', 'PRODSS'), ('COLIMITED', 'COLIMITED')], default=1, max_length=20),
        ),
    ]
