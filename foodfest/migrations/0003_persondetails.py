# Generated by Django 4.0.1 on 2022-01-31 11:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foodfest', '0002_alter_product_id_orderpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonDetails',
            fields=[
                ('person_id', models.AutoField(primary_key=True, serialize=False)),
                ('person_name', models.CharField(max_length=50)),
                ('phone', models.IntegerField(default=0)),
                ('address', models.CharField(max_length=50)),
                ('postal', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
