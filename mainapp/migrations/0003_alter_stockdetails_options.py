# Generated by Django 4.0.5 on 2022-06-20 05:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_alter_stockdetails_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockdetails',
            options={'verbose_name': 'Stock Details', 'verbose_name_plural': 'Stock Details'},
        ),
    ]