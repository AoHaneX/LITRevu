from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .forms import SignupForm


class HomeLoginView(LoginView):
    """
    Home page:
    - If user is authenticated → redirect to posts
    - Otherwise → display the login form (and the signup panel in the template)
    """

    template_name = "accounts/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("posts")
        return super().dispatch(request, *args, **kwargs)


class SignupView(CreateView):
    """
    Registration page: creates a new user account.
    After successful signup, we log the user in and redirect.
    """

    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        If the form is valid, save the user, log them in, then redirect.
        """
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
