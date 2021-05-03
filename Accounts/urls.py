from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from allauth.socialaccount.providers.google import urls as google_urls
from allauth.socialaccount.providers.facebook import urls as facebook_urls
from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('token/', token_send, name="token_send"),
    path('success/', success, name='success'),
    path('verify/<auth_token>', verify, name="verify"),
    path('error/', error_page, name="error"),
    path('login/', login_view, name='login'),
    path('accounts/', include(google_urls)),
    path('accounts/', include(facebook_urls)),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html'), name='password_change'),
    path('change_password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),
    path('my_account/',  login_required(UserUpdateView.as_view()), name='my_account'),
    path('user/<int:user_id>/', user_account, name='user_account'),
    path('users/', users_list, name='users_list'),
    path('user/<int:user_id>/follow/', follow_user, name='follow_user'),
    path('user/<int:user_id>/followers/', followers_list, name="followers_list"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
