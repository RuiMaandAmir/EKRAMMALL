# Generated by Django 5.2.1 on 2025-05-13 03:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_memberlevel_alter_withdrawalrecord_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="withdrawalrecord",
            name="account_holder",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="开户人姓名"
            ),
        ),
        migrations.AddField(
            model_name="withdrawalrecord",
            name="bank_account",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="银行账号"
            ),
        ),
        migrations.AddField(
            model_name="withdrawalrecord",
            name="bank_name",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="银行名称"
            ),
        ),
    ]
