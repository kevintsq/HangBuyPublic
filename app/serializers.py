from django.contrib.auth import password_validation
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Product, PurchaseDemand, ProductComment, DemandComment, UserModel, UserInfo, UserComment,\
    ProductOrder, DemandOrder, ChatMessage, SystemMessage, ProductComplaint, DemandComplaint, SystemFeedback


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("is_hidden",)

    seller_fullname = serializers.SerializerMethodField(read_only=True)
    seller_avatar = serializers.SerializerMethodField(read_only=True)

    def get_seller_fullname(self, obj):
        return obj.seller.last_name + obj.seller.first_name

    def get_seller_avatar(self, obj):
        avatar = get_object_or_404(UserInfo, user=obj.seller).avatar
        return avatar.url if avatar else None


class DemandSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDemand
        exclude = ("is_hidden",)

    demander_fullname = serializers.SerializerMethodField(read_only=True)
    demander_avatar = serializers.SerializerMethodField(read_only=True)

    def get_demander_fullname(self, obj):
        return obj.demander.last_name + obj.demander.first_name

    def get_demander_avatar(self, obj):
        avatar = get_object_or_404(UserInfo, user=obj.demander).avatar
        return avatar.url if avatar else None


class ProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        exclude = ("is_hidden",)

    commenter_fullname = serializers.SerializerMethodField(read_only=True)
    commenter_avatar = serializers.SerializerMethodField(read_only=True)

    def get_commenter_fullname(self, obj):
        return obj.commenter.last_name + obj.commenter.first_name

    def get_commenter_avatar(self, obj):
        avatar = get_object_or_404(UserInfo, user=obj.commenter).avatar
        return avatar.url if avatar else None


class DemandCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandComment
        exclude = ("is_hidden",)

    commenter_fullname = serializers.SerializerMethodField(read_only=True)
    commenter_avatar = serializers.SerializerMethodField(read_only=True)

    def get_commenter_fullname(self, obj):
        return obj.commenter.last_name + obj.commenter.first_name

    def get_commenter_avatar(self, obj):
        avatar = get_object_or_404(UserInfo, user=obj.commenter).avatar
        return avatar.url if avatar else None


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("username", "password", "email", "first_name", "last_name")
        extra_kwargs = {"password": {"write_only": True},
                        "email": {"required": True},
                        "first_name": {"required": True},
                        "last_name": {"required": True}}

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    # def validate(self, data):
    #     try:
    #         password_validation.validate_password(data.get("password"))
    #     except exceptions.ValidationError as e:
    #         raise serializers.ValidationError({"password": e.messages})
    #     return super().validate(data)

    def create(self, validated_data):
        user = UserModel.objects.create(**validated_data)
        user.set_password(validated_data.get("password"))
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("password", )
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance

    # def validate(self, data):
    #     try:
    #         password_validation.validate_password(data.get("password"))
    #     except exceptions.ValidationError as e:
    #         raise serializers.ValidationError({"password": e.messages})
    #     return super().validate(data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("id", "username", "email", "first_name", "last_name")


class UserInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    product_cnt = serializers.SerializerMethodField(read_only=True)
    purchase_cnt = serializers.SerializerMethodField(read_only=True)
    demand_cnt = serializers.SerializerMethodField(read_only=True)
    provide_cnt = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInfo
        fields = "__all__"

    def get_product_cnt(self, instance):
        return Product.objects.filter(seller=instance.user).count()

    def get_purchase_cnt(self, instance):
        return ProductOrder.objects.filter(buyer=instance.user).count()

    def get_demand_cnt(self, instance):
        return PurchaseDemand.objects.filter(demander=instance.user).count()

    def get_provide_cnt(self, instance):
        return DemandOrder.objects.filter(seller=instance.user).count()

    def update(self, instance, validated_data):
        if "user" in validated_data:
            user_data = validated_data["user"]
            user = instance.user
            user.username = user_data.get("username", user.username)
            user.email = user_data.get("email", user.email)
            user.first_name = user_data.get("first_name", user.first_name)
            user.last_name = user_data.get("last_name", user.last_name)
            user.save()
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)
        instance.wxid = validated_data.get("wxid", instance.wxid)
        instance.qq = validated_data.get("qq", instance.qq)
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance


class UserCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserComment
        exclude = ("is_hidden",)

    commenter_fullname = serializers.SerializerMethodField(read_only=True)
    commenter_avatar = serializers.SerializerMethodField(read_only=True)

    def get_commenter_fullname(self, obj):
        return obj.commenter.last_name + obj.commenter.first_name

    def get_commenter_avatar(self, obj):
        avatar = get_object_or_404(UserInfo, user=obj.commenter).avatar
        return avatar.url if avatar else None


class ProductOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)

    class Meta:
        model = ProductOrder
        fields = "__all__"


class DemandOrderSerializer(serializers.ModelSerializer):
    demand = DemandSerializer(required=False)

    class Meta:
        model = DemandOrder
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"


class SystemMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMessage
        fields = "__all__"


class ProductComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComplaint
        fields = "__all__"


class DemandComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandComplaint
        fields = "__all__"


class SystemFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemFeedback
        fields = "__all__"
