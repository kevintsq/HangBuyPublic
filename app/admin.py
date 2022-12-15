# -*- coding: UTF-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, UserAdmin
from import_export.admin import ImportExportModelAdmin
from .resources import *

admin.site.site_header = "HangBuy 管理"
admin.site.site_title = "HangBuy 站点管理"


class UserInfoInline(admin.StackedInline):
    model = UserInfo
    can_delete = False


# Define a new User admin and re-register it
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserInfoInline,)
    list_display = ('id',) + UserAdmin.list_display
    search_fields = ('username', 'first_name', 'last_name')


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('product_id', 'name', 'category', 'price', 'seller', 'create_time', 'sold_out', 'is_hidden')
    list_filter = ('category', 'sold_out', 'is_hidden')
    search_fields = ('name', 'description')
    
    def save_model(self, request, obj, form, change):
        if change and "is_hidden" in form.changed_data:
            if obj.is_hidden:
                SystemMessage.objects.create(user=obj.seller, content="您的商品因故已被隐藏。")
            else:
                SystemMessage.objects.create(user=obj.seller, content="您被隐藏的商品已被恢复。")
        super().save_model(request, obj, form, change)


@admin.register(PurchaseDemand)
class PurchaseDemandAdmin(ImportExportModelAdmin):
    resource_class = DemandResource
    list_display = ('demand_id', 'name', 'category', 'price', 'demander', 'create_time', 'is_met', 'is_hidden')
    list_filter = ('category', 'is_met', 'is_hidden')
    search_fields = ('name', 'description')

    def save_model(self, request, obj, form, change):
        if change and "is_hidden" in form.changed_data:
            if obj.is_hidden:
                SystemMessage.objects.create(user=obj.demander, content="您的求购品因故已被隐藏。")
            else:
                SystemMessage.objects.create(user=obj.demander, content="您被隐藏的求购品已被恢复。")
        super().save_model(request, obj, form, change)


@admin.register(ProductComment)
class ProductCommentAdmin(ImportExportModelAdmin):
    resource_class = ProductCommentResource
    list_display = ('comment_id', 'content', 'product', 'commenter', 'review_comment', 'create_time', 'is_hidden')
    list_filter = ('is_hidden',)
    search_fields = ('content',)

    def save_model(self, request, obj, form, change):
        if change and "is_hidden" in form.changed_data:
            if obj.is_hidden:
                SystemMessage.objects.create(user=obj.commenter, content="您的商品评论因故已被隐藏。")
            else:
                SystemMessage.objects.create(user=obj.commenter, content="您被隐藏的商品评论已被恢复。")
        super().save_model(request, obj, form, change)


@admin.register(DemandComment)
class DemandCommentAdmin(ImportExportModelAdmin):
    resource_class = DemandCommentResource
    list_display = ('comment_id', 'content', 'demand', 'commenter', 'review_comment', 'create_time', 'is_hidden')
    list_filter = ('is_hidden',)
    search_fields = ('content',)

    def save_model(self, request, obj, form, change):
        if change and "is_hidden" in form.changed_data:
            if obj.is_hidden:
                SystemMessage.objects.create(user=obj.commenter, content="您的求购品评论因故已被隐藏。")
            else:
                SystemMessage.objects.create(user=obj.commenter, content="您被隐藏的求购品评论已被恢复。")
        super().save_model(request, obj, form, change)


@admin.register(UserInfo)
class UserInfoAdmin(ImportExportModelAdmin):
    resource_class = UserInfoResource
    list_display = ('user', 'nickname', 'phone_number', 'wxid', 'qq')
    search_fields = ('nickname', 'phone_number', 'wxid', 'qq')


@admin.register(UserComment)
class UserCommentAdmin(ImportExportModelAdmin):
    resource_class = UserCommentResource
    list_display = ('comment_id', 'content', 'user', 'commenter', 'review_comment', 'create_time', 'is_hidden')
    list_filter = ('is_hidden',)
    search_fields = ('content',)

    def save_model(self, request, obj, form, change):
        if change and "is_hidden" in form.changed_data:
            if obj.is_hidden:
                SystemMessage.objects.create(user=obj.commenter, content="您对用户的评论因故已被隐藏。")
            else:
                SystemMessage.objects.create(user=obj.commenter, content="您被隐藏的对用户的评论已被恢复。")
        super().save_model(request, obj, form, change)


@admin.register(ProductOrder)
class ProductOrderAdmin(ImportExportModelAdmin):
    resource_class = ProductOrderResource
    list_display = ('order_id', 'buyer', 'product', 'create_time', 'finish_time')


@admin.register(DemandOrder)
class DemandOrderAdmin(ImportExportModelAdmin):
    resource_class = DemandOrderResource
    list_display = ('order_id', 'seller', 'demand', 'create_time', 'finish_time')


@admin.register(ChatMessage)
class ChatMessageAdmin(ImportExportModelAdmin):
    resource_class = ChatMessageResource
    list_display = ('message_id', 'content', 'sender', 'receiver', 'create_time', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('content',)


@admin.register(SystemMessage)
class SystemMessageAdmin(ImportExportModelAdmin):
    resource_class = SystemMessageResource
    list_display = ('message_id', 'content', 'user', 'create_time', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('content',)


@admin.register(ProductComplaint)
class ProductComplaintAdmin(ImportExportModelAdmin):
    resource_class = ProductComplaintResource
    list_display = ('complaint_id', 'complaint', 'product', 'user', 'create_time')
    search_fields = ('complaint',)


@admin.register(DemandComplaint)
class DemandComplaintAdmin(ImportExportModelAdmin):
    resource_class = DemandComplaintResource
    list_display = ('complaint_id', 'complaint', 'demand', 'user', 'create_time')
    search_fields = ('complaint',)


@admin.register(SystemFeedback)
class SystemFeedbackAdmin(ImportExportModelAdmin):
    resource_class = SystemFeedbackResource
    list_filter = ('category',)
    list_display = ('feedback_id', 'content', 'category', 'user', 'create_time')
    search_fields = ('content',)
