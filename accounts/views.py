from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm


class SignupView(CreateView):
    """
    Registration page: creates a new user account.
    After successful signup, we log the user in and redirect.
    """
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("home")  #TO check -- Can  change later to  another page   

    def form_valid(self, form):
        """
        If the form is valid, save the user, log them in, then redirect.
        """
        response = super().form_valid(form)
        login(self.request, self.object)
        return response