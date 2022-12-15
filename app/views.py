"""
Definition of views.
"""
import json
from datetime import datetime

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpRequest
from django.utils.timezone import now
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from .permissions import IsNotAuthenticated
from .serializers import *


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )


def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    product_list = Product.objects
    return render(
        request,
        'app/contact.html',
        {
            'title': 'Contact',
            'message': 'Your contact page.',
            'year': datetime.now().year,
            'product_list': product_list
        }
    )


def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About',
            'message': 'Your application description page.',
            'year': datetime.now().year,
        }
    )


class LoginView(APIView):
    permission_classes = (IsNotAuthenticated,)

    def post(self, request):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user is not None:
            login(request, user)
            info = UserInfo.objects.get(user=user)
            serializer = UserInfoSerializer(info)
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": "登录失败。"}, status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "登出成功。"}, status.HTTP_200_OK)


class RegistrationView(APIView):
    permission_classes = (IsNotAuthenticated,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            info = UserInfo.objects.create(user=user)
            user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
            login(request, user)
            serializer = UserInfoSerializer(info)
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request):
        if request.user.check_password(request.data.get("old_password")):
            serializer = ChangePasswordSerializer(request.user, request.data)
            if serializer.is_valid():
                serializer.save()
                # Updating the password logs out all other sessions for the user
                # except the current one.
                update_session_auth_hash(request, request.user)
                return Response({"detail": "密码修改成功。"}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "旧密码不正确。"}, status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id=None):
        if user_id:
            item = get_object_or_404(UserInfo, user=user_id)
        else:
            item = UserInfo.objects.get(user=request.user)
        serializer = UserInfoSerializer(item)
        return Response({"detail": serializer.data}, status.HTTP_200_OK)

    def patch(self, request, user_id=None):
        item = UserInfo.objects.get(user=request.user)
        if "user" in request.data:
            try:
                user = json.loads(request.data.get("user"))
            except:
                return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(request.user, user, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        if "avatar" in request.data:
            item.avatar.delete(False)  # no need to save here because the instance will be updated
        serializer = UserInfoSerializer(item, request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)


def paging(items, params: dict):
    cnt = len(items)  # if the amount is low, it's OK to use `len` because we may need to slice them
    # but if the amount is high, we may need to use `items.count()` because it may be more efficient
    if "pagesize" in params and "page" in params:
        pagesize = int(params["pagesize"])
        page = int(params["page"])
        if pagesize < cnt:
            end = pagesize * page
            start = end - pagesize
            if start >= cnt:
                raise ValueError("没有那么多页。")
            if end < cnt:
                items = items[end - pagesize:end]
            else:
                items = items[end - pagesize:cnt]
    return cnt, items


class UserProductView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        items = Product.objects.all().filter(is_hidden=False, seller=request.user)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)


class UserDemandView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        items = PurchaseDemand.objects.all().filter(is_hidden=False, demander=request.user)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = DemandSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)


class ChatView(APIView):
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id=None):
        if user_id:
            if request.accepted_renderer.format == 'html':
                r = Response(None, status.HTTP_200_OK, 'app/chat.html')
            else:
                sent = ChatMessage.objects.filter(sender=request.user, receiver=user_id)
                received = ChatMessage.objects.filter(sender=user_id, receiver=request.user)
                serializer = ChatMessageSerializer(sent | received, many=True)
                r = Response({"detail": serializer.data}, status.HTTP_200_OK)
                received.update(is_read=True)
        else:
            sent = ChatMessage.objects.filter(sender=request.user)
            received = ChatMessage.objects.filter(receiver=request.user)
            serializer = ChatMessageSerializer(sent | received, many=True)
            r = Response({"detail": serializer.data}, status.HTTP_200_OK)
        return r


class ProductInfoView(APIView):
    def get(self, request, product_id=None):
        if product_id:
            item = get_object_or_404(Product, product_id=product_id)
            if not item.is_hidden:
                serializer = ProductSerializer(item)
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": "商品因故已被隐藏。"}, status.HTTP_400_BAD_REQUEST)
        else:
            items = Product.objects.all().filter(is_hidden=False, sold_out=False)
            params: dict = request.query_params
            if "category" in params:
                items = items.filter(category=params["category"])
            if "search" in params:
                items = items.filter(name__icontains=params["search"]) | \
                        items.filter(description__icontains=params["search"])
            try:
                cnt, items = paging(items, params)
            except:
                return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
            serializer = ProductSerializer(items, many=True)
            return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, product_id=None):
        serializer = ProductSerializer(data=request.data, allow_null=False)
        if serializer.is_valid():
            serializer.save(seller=request.user, sold_out=False)
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id=None):
        if product_id:
            item = get_object_or_404(Product, product_id=product_id)
            if item.seller == request.user:
                if "image" in request.data:
                    item.image.delete(False)  # no need to save here because the instance will be updated
                serializer = ProductSerializer(item, request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"detail": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "您只能修改自己的商品信息。"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "您必须指定要修改的商品。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id=None):
        item = get_object_or_404(Product, product_id=product_id)
        if item.seller == request.user:
            item.image.delete(False)  # no need to save here because the instance will be deleted
            item.delete()
            return Response({"detail": "商品信息删除成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的商品信息。"}, status.HTTP_400_BAD_REQUEST)


class DemandInfoView(APIView):
    def get(self, request, demand_id=None):
        if demand_id:
            item = get_object_or_404(PurchaseDemand, demand_id=demand_id)
            if not item.is_hidden:
                serializer = DemandSerializer(item)
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": "求购信息因故已被隐藏。"}, status.HTTP_400_BAD_REQUEST)
        else:
            items = PurchaseDemand.objects.all().filter(is_hidden=False, is_met=False)
            params: dict = request.query_params
            if "category" in params:
                items = items.filter(category=params["category"])
            if "search" in params:
                items = items.filter(name__icontains=params["search"]) | \
                        items.filter(description__icontains=params["search"])
            try:
                cnt, items = paging(items, params)
            except:
                return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
            serializer = DemandSerializer(items, many=True)
            return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, demand_id=None):
        serializer = DemandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(demander=request.user, is_met=False)
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, demand_id=None):
        if demand_id:
            item = get_object_or_404(PurchaseDemand, demand_id=demand_id)
            if item.demander == request.user:
                serializer = DemandSerializer(item, request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"detail": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "您只能修改自己的求购信息。"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "您必须指定要修改的求购品。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, demand_id=None):
        item = get_object_or_404(PurchaseDemand, demand_id=demand_id)
        if item.demander == request.user:
            item.delete()
            return Response({"detail": "求购信息删除成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的求购信息。"}, status.HTTP_400_BAD_REQUEST)


class ProductCommentView(APIView):
    def get(self, request, product_id, comment_id=None):
        items = get_list_or_404(ProductComment, product=product_id, is_hidden=False)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = ProductCommentSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, product_id, comment_id=None):
        product = get_object_or_404(Product, product_id=product_id)
        serializer = ProductCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(product=product, commenter=request.user)
            SystemMessage.objects.create(user=comment.product.seller, content="您的商品有一条新评论。")
            if comment.review_comment:
                SystemMessage.objects.create(user=comment.review_comment.commenter, content="您的评论有一条新回复。")
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id, comment_id=None):
        item = get_object_or_404(ProductComment, comment_id=comment_id)
        if item.commenter == request.user:
            serializer = ProductCommentSerializer(item, request.data, partial=True)
            if serializer.is_valid():
                comment = serializer.save()
                SystemMessage.objects.create(user=comment.product.seller, content="您的商品有一条评论被修改。")
                if comment.review_comment:
                    SystemMessage.objects.create(user=comment.review_comment.commenter, content="您有一条评论回复被修改。")
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "您只能修改自己的评论。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id, comment_id=None):
        item = get_object_or_404(ProductComment, comment_id=comment_id)
        if item.commenter == request.user:
            item.delete()
            return Response({"detail": "商品评论删除成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的评论。"}, status.HTTP_400_BAD_REQUEST)


class DemandCommentView(APIView):
    def get(self, request, demand_id, comment_id=None):
        items = get_list_or_404(DemandComment, demand=demand_id, is_hidden=False)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = DemandCommentSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, demand_id, comment_id=None):
        demand = get_object_or_404(PurchaseDemand, demand_id=demand_id)
        serializer = DemandCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(demand=demand, commenter=request.user)
            SystemMessage.objects.create(user=comment.demand.demander, content="您的求购品有一条新评论。")
            if comment.review_comment:
                SystemMessage.objects.create(user=comment.review_comment.commenter, content="您的评论有一条新回复。")
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, demand_id, comment_id=None):
        item = get_object_or_404(DemandComment, comment_id=comment_id)
        if item.commenter == request.user:
            serializer = DemandCommentSerializer(item, request.data, partial=True)
            if serializer.is_valid():
                comment = serializer.save()
                SystemMessage.objects.create(user=comment.demand.demander, content="您的求购品有一条评论被修改。")
                if comment.review_comment:
                    SystemMessage.objects.create(user=comment.review_comment.commenter, content="您有一条评论回复被修改。")
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "您只能修改自己的评论。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, demand_id, comment_id=None):
        item = get_object_or_404(DemandComment, comment_id=comment_id)
        if item.commenter == request.user:
            item.delete()
            return Response({"detail": "求购品评论删除成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的评论。"}, status.HTTP_400_BAD_REQUEST)


UserModel = get_user_model()


class UserCommentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id, comment_id=None):
        items = get_list_or_404(UserComment, user_id=user_id, is_hidden=False)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = UserCommentSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, user_id, comment_id=None):
        user = get_object_or_404(UserModel, id=user_id)
        serializer = UserCommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(user=user, commenter=request.user)
            SystemMessage.objects.create(user=comment.user, content="您有一条新评论。")
            if comment.review_comment:
                SystemMessage.objects.create(user=comment.review_comment.commenter, content="您有一条评论被回复。")
            return Response({"detail": serializer.data}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id, comment_id=None):
        item = get_object_or_404(UserComment, comment_id=comment_id)
        if item.commenter == request.user:
            serializer = UserCommentSerializer(item, request.data, partial=True)
            if serializer.is_valid():
                comment = serializer.save()
                SystemMessage.objects.create(user=comment.user, content="您有一条评论被修改。")
                if comment.review_comment:
                    SystemMessage.objects.create(user=comment.review_comment.commenter, content="您有一条评论回复被修改。")
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "您只能修改自己的评论。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, comment_id=None):
        item = get_object_or_404(UserComment, comment_id=comment_id)
        if item.commenter == request.user:
            item.delete()
            return Response({"detail": "用户评论删除成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的评论。"}, status.HTTP_400_BAD_REQUEST)


class ProductOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id=None):
        items = ProductOrder.objects.all().filter(buyer=request.user)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = ProductOrderSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, order_id=None):
        """place order"""
        product = get_object_or_404(Product, product_id=request.data.pop("product", None))
        if product.sold_out or product.is_hidden:
            return Response({"detail": "您只能购买未卖出的商品。"}, status.HTTP_400_BAD_REQUEST)
        else:
            serializer = ProductOrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(buyer=request.user, product=product)
                SystemMessage.objects.create(user=product.seller, content="您的商品已卖出，请及时与买方联系。")
                product.sold_out = True
                product.save()
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id=None):
        item = get_object_or_404(ProductOrder, order_id=order_id)
        if item.buyer == request.user:
            item.finish_time = now()
            item.save()
            return Response({"detail": ProductOrderSerializer(item).data}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能完成自己的订单。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id=None):
        order = get_object_or_404(ProductOrder, order_id=order_id)
        if order.buyer == request.user:
            if order.finish_time is None:  # order has not finished yet
                SystemMessage.objects.create(user=order.product.seller, content="您商品的订单已被取消。")
                order.product.sold_out = False
                order.product.save()
                order.delete()
                return Response({"detail": "订单已成功取消。"}, status.HTTP_200_OK)
            else:
                order.delete()
                return Response({"detail": "订单已成功删除。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能取消或删除自己的订单。"}, status.HTTP_400_BAD_REQUEST)


class DemandOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id=None):
        items = DemandOrder.objects.all().filter(seller=request.user)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = DemandOrderSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def post(self, request, order_id=None):
        """place order"""
        demand = get_object_or_404(PurchaseDemand, demand_id=request.data.pop("demand", None))
        if demand.is_met or demand.is_hidden:
            return Response({"detail": "您只能出售他人需要的求购品。"}, status.HTTP_400_BAD_REQUEST)
        else:
            serializer = DemandOrderSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(seller=request.user, demand=demand)
                SystemMessage.objects.create(user=demand.demander, content="您的求购品已有卖方愿意提供，请及时与卖方联系。")
                demand.is_met = True
                demand.save()
                return Response({"detail": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id=None):
        item = get_object_or_404(DemandOrder, order_id=order_id)
        if item.seller == request.user:
            item.finish_time = now()
            item.save()
            return Response({"detail": DemandOrderSerializer(item).data}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能完成自己的订单。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id=None):
        order = get_object_or_404(DemandOrder, order_id=order_id)
        if order.seller == request.user:
            if order.finish_time is None:  # order has not finished yet
                SystemMessage.objects.create(user=order.demand.demander, content="您求购品的订单已被取消。")
                order.demand.is_met = False
                order.demand.save()
                order.delete()
                return Response({"detail": "订单已成功取消。"}, status.HTTP_200_OK)
            else:
                order.delete()
                return Response({"detail": "订单已成功删除。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能取消或删除自己的订单。"}, status.HTTP_400_BAD_REQUEST)


class SystemMessageView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id=None):
        items = SystemMessage.objects.all().filter(user=request.user)
        try:
            cnt, items = paging(items, request.query_params)
        except:
            return Response({"detail": "参数不正确。"}, status.HTTP_400_BAD_REQUEST)
        serializer = SystemMessageSerializer(items, many=True)
        return Response({"cnt": cnt, "detail": serializer.data}, status.HTTP_200_OK)

    def patch(self, request, message_id=None):
        item = get_object_or_404(SystemMessage, message_id=message_id)
        if item.user == request.user:
            item.is_read = True
            item.save()
            return Response({"detail": SystemMessageSerializer(item).data}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能将自己的系统消息设为已读。"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, message_id=None):
        item = get_object_or_404(SystemMessage, message_id=message_id)
        if item.user == request.user:
            item.delete()
            return Response({"detail": "系统消息已删除。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": "您只能删除自己的系统消息。"}, status.HTTP_400_BAD_REQUEST)


class ProductComplaintView(APIView):
    def post(self, request):
        serializer = ProductComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"detail": "商品投诉成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class DemandComplaintView(APIView):
    def post(self, request):
        serializer = DemandComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"detail": "求购品投诉成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)


class SystemFeedbackView(APIView):
    def post(self, request):
        serializer = SystemFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"detail": "系统反馈提交成功。"}, status.HTTP_200_OK)
        else:
            return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)
