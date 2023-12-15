from django.urls import path
from . import views

urlpatterns = [
    path('login_with_authenticator/',views.LoginWithAuthenticator,name='login_with_authenticator'),
    path('login_with_authenticator_google/',views.LoginWithAuthenticatorGoogle,name='login_with_authenticator_google'),
    path('signup/',views.SignupUser,name='signup'),
    path('signup_with_google/',views.SignupUserGoogle,name='signup_with_google'),
    path('confirm_email/',views.email_confirmed,name='email_confirmed'),
    path('login/',views.LoginUser,name='login'),
]
