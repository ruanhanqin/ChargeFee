from django.db import models
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.


class Charge(models.Model):
    choices_in = (
        ('欠费', '欠费'),
        ('已收费', '已收费')
    )
    cashier = models.ForeignKey(User, null=True, blank=True, verbose_name="收费员", on_delete=models.CASCADE,
                                related_name='cashier')
    write_book = models.CharField(max_length=32, null=True, blank=True, verbose_name="抄表册")
    account_number = models.CharField(max_length=32, null=True, blank=True, verbose_name="户号")
    account_name = models.CharField(max_length=256, null=True, blank=True, verbose_name="户名")
    user_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name="客户电话")
    address = models.CharField(max_length=256, default="", null=True, blank=True, verbose_name="用电地址")
    arrears = models.FloatField(default=0.0, null=True, blank=True, verbose_name="欠费金额")
    arrears_time = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="欠费时间")
    charges = models.FloatField(default=0.0, null=True, blank=True, verbose_name="收费金额")
    charge_time = models.DateTimeField(default='', blank=True, null=True, verbose_name="收费时间")
    bill_manager = models.ForeignKey(User, null=True, blank=True, verbose_name="票据管理员", on_delete=models.CASCADE,
                                     related_name='bill')
    in_arrears = models.CharField(max_length=8, choices=choices_in, null=True, blank=True, verbose_name="是否欠费")

    class Meta:
        verbose_name = "客户信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.account_name
