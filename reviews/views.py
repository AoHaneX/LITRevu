from django.shortcuts import render

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import TicketForm, ReviewForm
from .models import Ticket, Review
from django.views.generic import ListView


class IsOwnerMixin(UserPassesTestMixin):
    """
    Mixin to restrict update/delete actions to the object owner.
    """

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class TicketCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Ticket for the logged-in user.
    """
    model = Ticket
    form_class = TicketForm
    template_name = "reviews/ticket_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        Automatically assign the current user as the ticket author.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, IsOwnerMixin, UpdateView):
    """
    Update an existing Ticket (only allowed for the owner).
    """
    model = Ticket
    form_class = TicketForm
    template_name = "reviews/ticket_form.html"
    success_url = reverse_lazy("home")
    success_message = "Billet créé avec succès."

    def form_valid(self, form):
        """
        Automatically assign the current user as the ticket author.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketDeleteView(LoginRequiredMixin, IsOwnerMixin, DeleteView):
    """
    Delete an existing Ticket (only allowed for the owner).
    """
    model = Ticket
    template_name = "reviews/ticket_confirm_delete.html"
    success_url = reverse_lazy("home")
    success_message = "Billet modifié avec succès."


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new Review for a given Ticket.
    The ticket is provided via the URL.
    """
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("home")
    success_message = "Critique créée avec succès."

    def dispatch(self, request, *args, **kwargs):
        """
        Load the related ticket once and store it on the instance.
        """
        self.ticket = get_object_or_404(Ticket, pk=kwargs["ticket_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Automatically assign the current user and the target ticket.
        """
        form.instance.user = self.request.user
        form.instance.ticket = self.ticket
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Add the ticket to the template context for better UX.
        """
        context = super().get_context_data(**kwargs)
        context["ticket"] = self.ticket
        return context


class ReviewUpdateView(LoginRequiredMixin, IsOwnerMixin, UpdateView):
    """
    Update an existing Review (only allowed for the owner).
    """
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("home")
    success_message = "Critique modifiée avec succès."


class ReviewDeleteView(LoginRequiredMixin, IsOwnerMixin, DeleteView):
    """
    Delete an existing Review (only allowed for the owner).
    """
    model = Review
    template_name = "reviews/review_confirm_delete.html"
    success_url = reverse_lazy("home")

    from django.views.generic import ListView

class TicketListView(LoginRequiredMixin, ListView):
    """
    Display a list of tickets.
    For now, we show only the current user's tickets.
    """
    model = Ticket
    template_name = "reviews/ticket_list.html"
    context_object_name = "tickets"
    ordering = ["-time_created"]

    def get_queryset(self):
        """
        Return tickets created by the current user.
        """
        return Ticket.objects.filter(user=self.request.user).order_by("-time_created")