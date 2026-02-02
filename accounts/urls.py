from django.contrib.auth import views as auth_views
from django.urls import path

from .views import HomeLoginView, SignupView

urlpatterns = [
    # Public landing page: contains login form + signup CTA
    path("", HomeLoginView.as_view(), name="home"),

    # Auth endpoints
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", HomeLoginView.as_view(), name="login"),
]