# -*- coding: UTF-8 -*-

"""
Definition of models.  TODO: non-editable foreign key?
"""

from django.db import models
from django.core.validators import RegexValidator
from djmoney.money import Money
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from django.contrib.auth import get_user_model
from uuid import uuid4
from enum import auto
import os


UserModel = get_user_model()


def product_image_path(instance, filename):
    return f"product_img/{uuid4()}{os.path.splitext(filename)[-1]}"


def complaint_image_path(instance, filename):
    return f"complaint_img/{uuid4()}{os.path.splitext(filename)[-1]}"


def profile_image_path(instance, filename):
    return f"profile_img/{uuid4()}{os.path.splitext(filename)[-1]}"


class ProductCategory(models.IntegerChoices):
    衣服鞋袜 = auto()
    电子数码 = auto()
    课本书籍 = auto()
    桌椅家具 = auto()
    文具办公 = auto()
    运动户外 = auto()
    吃喝玩乐 = auto()
    其它 = auto()


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField("商品名称", max_length=64)
    create_time = models.DateTimeField("发布时间", auto_now_add=True)
    category = models.IntegerField("商品类别", choices=ProductCategory.choices)
    description = models.TextField("商品描述")
    image = models.ImageField("商品图片", upload_to=product_image_path)
    price = MoneyField("商品价格", max_digits=7, decimal_places=2,
                       validators=(MinMoneyValidator(Money(0, "CNY")),))
    seller = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="卖方")
    sold_out = models.BooleanField("已卖掉", default=False)
    is_hidden = models.BooleanField("隐藏", default=False)

    def __str__(self):
        return f"{self.name} ({self.product_id})"


class PurchaseDemand(models.Model):
    demand_id = models.BigAutoField(primary_key=True)
    name = models.CharField("求购品名", max_length=64)
    create_time = models.DateTimeField("求购时间", auto_now_add=True)
    category = models.IntegerField("求购品类别", choices=ProductCategory.choices)
    description = models.TextField("求购品描述")
    price = MoneyField("期望价格", max_digits=7, decimal_places=2,
                       validators=(MinMoneyValidator(Money(0, "CNY")),))
    demander = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="求购者")
    is_met = models.BooleanField("已满足", default=False)
    is_hidden = models.BooleanField("隐藏", default=False)

    def __str__(self):
        return f"{self.name} ({self.demand_id})"


class ProductComment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name="商品")
    commenter = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="评论者")
    review_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="回复评论")
    create_time = models.DateTimeField("评论时间", auto_now_add=True)
    content = models.TextField("评论内容")
    is_hidden = models.BooleanField("隐藏", default=False)

    def __str__(self):
        return f"{self.content} ({self.comment_id})"


class DemandComment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    demand = models.ForeignKey(PurchaseDemand, on_delete=models.CASCADE, default=None, verbose_name="求购品")
    commenter = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="评论者")
    review_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="回复评论")
    create_time = models.DateTimeField("评论时间", auto_now_add=True)
    content = models.TextField("评论内容")
    is_hidden = models.BooleanField("隐藏", default=False)

    def __str__(self):
        return f"{self.content} ({self.comment_id})"


class UserInfo(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, primary_key=True, verbose_name="用户")
    nickname = models.CharField("昵称", max_length=64, null=True, blank=True)
    avatar = models.ImageField("头像", upload_to=profile_image_path, null=True, blank=True)
    phone_number = models.CharField("手机号", max_length=11, null=True, blank=True,
                                    # validators=(RegexValidator(r"^1[3-9]\d{9}$"),))
                                    validators=(RegexValidator(r"^(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[0-35-9]\d{2}|4(?:0\d|1[0-2]|9\d))|9[0-35-9]\d{2}|6[2567]\d{2}|4[579]\d{2})\d{6}$"),))
    wxid = models.CharField("微信号", max_length=20, null=True, blank=True,
                            validators=(RegexValidator(r"^[a-zA-Z][\w-]{5,19}$"),))
    qq = models.CharField("QQ号", max_length=15, null=True, blank=True,
                          validators=(RegexValidator(r"^[1-9][0-9]{4,14}$"),))
    description = models.TextField("用户简介", null=True, blank=True)

    def __str__(self):
        return f"{self.user}"


class UserComment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="被评论者")
    commenter = models.ForeignKey(UserModel, related_name="commenter_id", on_delete=models.CASCADE, default=None, verbose_name="评论者")
    review_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="回复评论")
    create_time = models.DateTimeField("评论时间", auto_now_add=True)
    content = models.TextField("评论内容")
    is_hidden = models.BooleanField("隐藏", default=False)

    def __str__(self):
        return f"{self.content} ({self.comment_id})"


class ProductOrder(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    buyer = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="买方")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name="商品")
    create_time = models.DateTimeField("下单时间", auto_now_add=True)
    finish_time = models.DateTimeField("成交时间", null=True, blank=True)

    def __str__(self):
        return f"{self.product} ({self.order_id})"


class DemandOrder(models.Model):
    order_id = models.BigAutoField(primary_key=True)
    seller = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="卖方")
    demand = models.ForeignKey(PurchaseDemand, on_delete=models.CASCADE, default=None, verbose_name="买方")
    create_time = models.DateTimeField("下单时间", auto_now_add=True)
    finish_time = models.DateTimeField("成交时间", null=True, blank=True)

    def __str__(self):
        return f"{self.demand} ({self.order_id})"


class ChatMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(UserModel, related_name="sender_id", on_delete=models.CASCADE, default=None, verbose_name="发送者")
    receiver = models.ForeignKey(UserModel, related_name="receiver_id", on_delete=models.CASCADE, default=None, verbose_name="接收者")
    create_time = models.DateTimeField("发送时间", auto_now_add=True)
    content = models.TextField("消息内容")
    is_read = models.BooleanField("已读", default=False)

    def __str__(self):
        return f"{self.content} ({self.message_id})"


class SystemMessage(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="接收者")
    create_time = models.DateTimeField("发送时间", auto_now_add=True)
    content = models.TextField("消息内容")
    is_read = models.BooleanField("已读", default=False)

    def __str__(self):
        return f"{self.content} ({self.message_id})"


class ProductComplaint(models.Model):
    complaint_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="投诉者")
    create_time = models.DateTimeField("投诉时间", auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name="商品")
    complaint = models.TextField("投诉内容")
    image = models.ImageField("投诉图片", upload_to=complaint_image_path)

    def __str__(self):
        return f"{self.complaint} ({self.complaint_id})"


class DemandComplaint(models.Model):
    complaint_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="投诉者")
    create_time = models.DateTimeField("投诉时间", auto_now_add=True)
    demand = models.ForeignKey(PurchaseDemand, on_delete=models.CASCADE, default=None, verbose_name="求购品")
    complaint = models.TextField("投诉内容")

    def __str__(self):
        return f"{self.complaint} ({self.complaint_id})"


class SystemFeedback(models.Model):
    class FeedbackCategory(models.IntegerChoices):
        错误 = auto()
        改进 = auto()

    feedback_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, default=None, verbose_name="用户")
    create_time = models.DateTimeField("反馈时间", auto_now_add=True)
    category = models.IntegerField("反馈类型", choices=FeedbackCategory.choices)
    content = models.TextField("反馈内容")

    def __str__(self):
        return f"{self.content} ({self.feedback_id})"
