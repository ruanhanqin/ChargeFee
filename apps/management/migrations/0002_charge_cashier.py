# Generated by Django 2.1.3 on 2018-12-10 15:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='cashier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cashier', to=settings.AUTH_USER_MODEL, verbose_name='收费员'),
        ),
    ]
