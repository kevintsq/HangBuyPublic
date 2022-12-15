"""
Note that the imported data are only validated by the DBMS,
so please make sure that the data in the table are valid.
ID must be specified in the table.
"""

from .serializers import *
from import_export.resources import ModelResource


class ProductResource(ModelResource):
    class Meta:
        model = Product
        import_id_fields = ('product_id',)


class DemandResource(ModelResource):
    class Meta:
        model = PurchaseDemand
        import_id_fields = ('demand_id',)


class ProductCommentResource(ModelResource):
    class Meta:
        model = ProductComment
        import_id_fields = ('comment_id',)


class DemandCommentResource(ModelResource):
    class Meta:
        model = DemandComment
        import_id_fields = ('comment_id',)


class UserInfoResource(ModelResource):
    class Meta:
        model = UserInfo
        import_id_fields = ('user',)


class UserCommentResource(ModelResource):
    class Meta:
        model = UserComment
        import_id_fields = ('comment_id',)


class ProductOrderResource(ModelResource):
    class Meta:
        model = ProductOrder
        import_id_fields = ('order_id',)


class DemandOrderResource(ModelResource):
    class Meta:
        model = DemandOrder
        import_id_fields = ('order_id',)


class ChatMessageResource(ModelResource):
    class Meta:
        model = ChatMessage
        import_id_fields = ('message_id',)


class SystemMessageResource(ModelResource):
    class Meta:
        model = SystemMessage
        import_id_fields = ('message_id',)


class ProductComplaintResource(ModelResource):
    class Meta:
        model = ProductComplaint
        import_id_fields = ('complaint_id',)


class DemandComplaintResource(ModelResource):
    class Meta:
        model = DemandComplaint
        import_id_fields = ('complaint_id',)


class SystemFeedbackResource(ModelResource):
    class Meta:
        model = SystemFeedback
        import_id_fields = ('feedback_id',)
