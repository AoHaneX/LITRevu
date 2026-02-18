from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import TicketForm, ReviewForm, FollowUserForm
from .models import Ticket, Review, UserFollows
from django.views.generic import ListView, TemplateView


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

class ReviewListView(LoginRequiredMixin, ListView):
    """
    Display the list of reviews created by the current user.
    """
    model = Review
    template_name = "reviews/review_list.html"
    context_object_name = "reviews"
    ordering = ["-time_created"]

    def get_queryset(self):
        """
        Return only reviews created by the logged-in user.
        """
        return (
            Review.objects
            .filter(user=self.request.user)
            .select_related("ticket")
            .order_by("-time_created")
        )

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

User = get_user_model()


class FollowListView(LoginRequiredMixin, View):
    """
    Display the follow page:
    - following_relations: who the current user follows
    - suggested_users: users that the current user does not follow (excluding self)
    """
    template_name = "reviews/follow_list.html"

    def get(self, request):
        """
        Render the follow page with current follow relations and suggestions.
        """
        following_relations = (
            UserFollows.objects
            .filter(user=request.user)
            .select_related("followed_user")
            .order_by("followed_user__username")
        )

        followed_ids = following_relations.values_list("followed_user_id", flat=True)

        suggested_users = (
            User.objects
            .exclude(id=request.user.id)
            .exclude(id__in=followed_ids)
            .order_by("username")
        )

        form = FollowUserForm()

        context = {
            "following_relations": following_relations,
            "suggested_users": suggested_users,
            "form": form,
        }
        return render(request, self.template_name, context)


class FollowAddView(LoginRequiredMixin, View):
    """
    Handle follow creation by username (POST only).
    """

    def post(self, request):
        """
        Validate the username and create a follow relationship if possible.
        """
        form = FollowUserForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Veuillez saisir un nom d'utilisateur valide.")
            return redirect("follow_list")

        username = form.cleaned_data["username"].strip()

        # Try to find the target user
        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect("follow_list")

        # Prevent self-follow
        if target_user == request.user:
            messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
            return redirect("follow_list")

        # Prevent duplicate follow
        already_following = UserFollows.objects.filter(
            user=request.user,
            followed_user=target_user,
        ).exists()

        if already_following:
            messages.info(request, "Vous suivez déjà cet utilisateur.")
            return redirect("follow_list")

        # Create the follow relationship
        UserFollows.objects.create(
            user=request.user,
            followed_user=target_user,
        )
        messages.success(request, f"Vous suivez maintenant {target_user.username}.")
        return redirect("follow_list")


class FollowRemoveView(LoginRequiredMixin, View):
    """
    Handle unfollow action (POST only).
    """

    def post(self, request, follow_id):
        """
        Delete a follow relationship owned by the current user.
        """
        relation = get_object_or_404(UserFollows, pk=follow_id, user=request.user)
        followed_username = relation.followed_user.username
        relation.delete()
        messages.success(request, f"Vous ne suivez plus {followed_username}.")
        return redirect("follow_list")
    

class PostsView(LoginRequiredMixin, TemplateView):
    """
    Display a single page containing both:
    - the current user's tickets
    - the current user's reviews
    """
    template_name = "reviews/posts.html"

    def get_context_data(self, **kwargs):
        """
        Provide the user's tickets and reviews to the template.
        """
        context = super().get_context_data(**kwargs)

        context["tickets"] = (
            Ticket.objects
            .filter(user=self.request.user)
            .order_by("-time_created")
        )

        context["reviews"] = (
            Review.objects
            .filter(user=self.request.user)
            .select_related("ticket")
            .order_by("-time_created")
        )

        return context