# Generated by Django 3.0.3 on 2020-02-12 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.IntegerField(default=None, primary_key=True, serialize=False, unique=True)),
                ('data', models.TextField(default=None)),
                ('status', models.TextField(default='Open')),
            ],
        ),
        migrations.CreateModel(
            name='Shipments',
            fields=[
                ('shipmentId', models.TextField(default=None, primary_key=True, serialize=False, unique=True)),
                ('data', models.TextField(default=None, null=True)),
                ('category', models.TextField(default=None)),
                ('shipmentDate', models.TextField()),
                ('shipmentItems', models.TextField(default=None)),
                ('transportId', models.TextField(default=None)),
            ],
        ),
    ]
