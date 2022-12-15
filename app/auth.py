# The views used below are normally mapped in the AdminSite instance.
# This URLs file is used to provide a reliable view deployment for test purposes.
# It is also provided as a convenience to those who want to deploy these URLs
# elsewhere.
from datetime import datetime

from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import path

from . import forms


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


# class CsrfExemptLoginView(views.LoginView):
#     """A LoginView with no CSRF protection."""
#
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         if self.redirect_authenticated_user and self.request.user.is_authenticated:
#             redirect_to = self.get_success_url()
#             if redirect_to == self.request.path:
#                 raise ValueError("Redirection loop for authenticated user detected. Check that "
#                                  "your LOGIN_REDIRECT_URL doesn't point to a login page.")
#             return HttpResponseRedirect(redirect_to)
#         return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    path('login/', views.LoginView.as_view(
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Log in',
                 'year': datetime.now().year,
             }
         ), name='login'),
    path('logout/', views.LogoutView.as_view(next_page='/api/'), name='logout'),

    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
