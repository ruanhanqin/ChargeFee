from django.db import models

# Create your models here.
from datetime import datetime
from django.contrib.auth.models import AbstractUser


# Create your models here.
# 自带的User一般无法满足需求,需要进行扩展


class UserProfile(AbstractUser):
    """
    用户表
    """
    GENDER_CHOICES = (
        ("male", "男"),
        ("female", "女")
    )
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生日期")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="female", verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")
    is_bill = models.BooleanField(default=False, verbose_name="是否票据管理员")
    is_charge = models.BooleanField(default=False, verbose_name="是否可以收费")
    is_check_charge = models.BooleanField(default=False, verbose_name="是否可以查询收费")
    is_check_arrears = models.BooleanField(default=False, verbose_name="是否可以查询欠费")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name if self.name else self.username
