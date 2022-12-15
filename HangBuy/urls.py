"""
Definition of urls for HangBuy.
"""

from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework import routers

from . import settings
from app import auth, views


urlpatterns = [
    path('', RedirectView.as_view(url='api/', permanent=True)),
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('app/img/favicon.ico'), permanent=True)),
    path('api/', include(
            [
                path('', views.home, name='home'),
                path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('app/img/favicon.ico'), permanent=True)),
                path('auth/', include(auth.urlpatterns)),
                path('contact/', views.contact, name='contact'),
                path('about/', views.about, name='about'),
                path('admin/', admin.site.urls),
                path('user/login/', views.LoginView.as_view()),
                path('user/logout/', views.LogoutView.as_view()),
                path('user/change-password/', views.ChangePasswordView.as_view()),
                path('user/register/', views.RegistrationView.as_view()),
                path('user/', views.UserInfoView.as_view()),
                path('user/<int:user_id>/', views.UserInfoView.as_view()),
                path('user/<int:user_id>/chat/', views.ChatView.as_view()),
                path('user/message/chat/', views.ChatView.as_view()),
                path('user/<int:user_id>/comment/', views.UserCommentView.as_view()),
                path('user/<int:user_id>/comment/<int:comment_id>/', views.UserCommentView.as_view()),
                path('user/product/', views.UserProductView.as_view()),
                path('user/product/order/', views.ProductOrderView.as_view()),
                path('user/product/order/<int:order_id>/', views.ProductOrderView.as_view()),
                path('user/demand/', views.UserDemandView.as_view()),
                path('user/demand/order/', views.DemandOrderView.as_view()),
                path('user/demand/order/<int:order_id>/', views.DemandOrderView.as_view()),
                path('user/message/system/', views.SystemMessageView.as_view()),
                path('user/message/system/<int:message_id>/', views.SystemMessageView.as_view()),
                path('product/', views.ProductInfoView.as_view()),
                path('product/<int:product_id>/', views.ProductInfoView.as_view()),
                path('product/<int:product_id>/comment/', views.ProductCommentView.as_view()),
                path('product/<int:product_id>/comment/<int:comment_id>/', views.ProductCommentView.as_view()),
                path('product/complain/', views.ProductComplaintView.as_view()),
                path('demand/', views.DemandInfoView.as_view()),
                path('demand/<int:demand_id>/', views.DemandInfoView.as_view()),
                path('demand/<int:demand_id>/comment/', views.DemandCommentView.as_view()),
                path('demand/<int:demand_id>/comment/<int:comment_id>/', views.DemandCommentView.as_view()),
                path('demand/complain/', views.DemandComplaintView.as_view()),
                path('feedback/', views.SystemFeedbackView.as_view())
            ]
        )
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
