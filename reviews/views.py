from itertools import chain

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from .forms import FollowUserForm, ReviewForm, TicketForm
from .models import Review, Ticket, UserFollows


User = get_user_model()


class IsOwnerMixin(UserPassesTestMixin):
    """
    Mixin to restrict update/delete actions to the object owner.
    """

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class TicketCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Create a new Ticket for the logged-in user.
    """

    model = Ticket
    form_class = TicketForm
    template_name = "reviews/ticket_form.html"
    success_url = reverse_lazy("posts")
    success_message = "Billet créé avec succès."

    def form_valid(self, form):
        """
        Automatically assign the current user as the ticket author.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(
    LoginRequiredMixin,
    IsOwnerMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """
    Update an existing Ticket (only allowed for the owner).
    """

    model = Ticket
    form_class = TicketForm
    template_name = "reviews/ticket_form.html"
    success_url = reverse_lazy("posts")
    success_message = "Billet modifié avec succès."

    def form_valid(self, form):
        """
        Automatically assign the current user as the ticket author.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketDeleteView(
    LoginRequiredMixin,
    IsOwnerMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """
    Delete an existing Ticket (only allowed for the owner).
    """

    model = Ticket
    template_name = "reviews/ticket_confirm_delete.html"
    success_url = reverse_lazy("posts")
    success_message = "Billet supprimé avec succès."


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
            Review.objects.filter(user=self.request.user)
            .select_related("ticket")
            .order_by("-time_created")
        )


class ReviewCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Create a new Review for a given Ticket.
    The ticket is provided via the URL.
    """

    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("posts")
    success_message = "Critique créée avec succès."

    def dispatch(self, request, *args, **kwargs):
        """
        Load the related ticket once and store it on the instance.
        """
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.ticket = get_object_or_404(Ticket, pk=kwargs["ticket_id"])
        if Review.objects.filter(ticket=self.ticket, user=request.user).exists():
            messages.info(request, "Vous avez déjà publié une critique pour ce billet.")
            return redirect("feed")
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


class ReviewUpdateView(
    LoginRequiredMixin,
    IsOwnerMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """
    Update an existing Review (only allowed for the owner).
    """

    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("posts")
    success_message = "Critique modifiée avec succès."

    def get_context_data(self, **kwargs):
        """
        Add the related ticket to the template context to display a preview.
        """
        context = super().get_context_data(**kwargs)
        context["ticket"] = self.object.ticket
        return context


class ReviewDeleteView(
    LoginRequiredMixin,
    IsOwnerMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """
    Delete an existing Review (only allowed for the owner).
    """

    model = Review
    template_name = "reviews/review_confirm_delete.html"
    success_url = reverse_lazy("posts")
    success_message = "Critique supprimée avec succès."


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
            UserFollows.objects.filter(user=request.user)
            .select_related("followed_user")
            .order_by("followed_user__username")
        )

        followed_ids = following_relations.values_list("followed_user_id", flat=True)

        suggested_users = (
            User.objects.exclude(id=request.user.id)
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

        _, created = UserFollows.objects.get_or_create(
            user=request.user,
            followed_user=target_user,
        )

        if not created:
            messages.info(request, "Vous suivez déjà cet utilisateur.")
            return redirect("follow_list")

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

        context["tickets"] = Ticket.objects.filter(user=self.request.user).order_by(
            "-time_created"
        )

        context["reviews"] = (
            Review.objects.filter(user=self.request.user)
            .select_related("ticket")
            .order_by("-time_created")
        )

        return context


class TicketReviewCreateView(LoginRequiredMixin, View):
    """
    Create a Ticket and a Review in a single form submission.
    """

    template_name = "reviews/ticket_review_form.html"

    def get(self, request):
        """
        Display empty forms for both Ticket and Review.
        """
        ticket_form = TicketForm()
        review_form = ReviewForm()
        return render(
            request,
            self.template_name,
            {"ticket_form": ticket_form, "review_form": review_form},
        )

    def post(self, request):
        """
        Validate both forms and create Ticket + Review in one transaction.
        """
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)

        if ticket_form.is_valid() and review_form.is_valid():
            with transaction.atomic():
                ticket = ticket_form.save(commit=False)
                ticket.user = request.user
                ticket.save()

                review = review_form.save(commit=False)
                review.user = request.user
                review.ticket = ticket
                review.save()

            messages.success(request, "Billet et critique créés avec succès.")
            return redirect("posts")

        # If at least one form is invalid, show errors
        return render(
            request,
            self.template_name,
            {"ticket_form": ticket_form, "review_form": review_form},
        )


class FeedView(LoginRequiredMixin, TemplateView):
    """
    Display a feed containing both Tickets and Reviews from:
    - the current user
    - users followed by the current user
    """

    template_name = "reviews/feed.html"

    def get_context_data(self, **kwargs):
        """
        Build a mixed list of posts (tickets + reviews) ordered by time.
        Also annotate tickets with a boolean telling if the current user already reviewed it.
        """
        context = super().get_context_data(**kwargs)

        # Users allowed in feed: self + followed users
        followed_ids = UserFollows.objects.filter(user=self.request.user).values_list(
            "followed_user_id", flat=True
        )

        allowed_user_ids = list(followed_ids) + [self.request.user.id]

        # Subquery: does the current user already have a review for this ticket?
        user_review_exists = Review.objects.filter(
            ticket=OuterRef("pk"),
            user=self.request.user,
        )

        tickets = (
            Ticket.objects.filter(user_id__in=allowed_user_ids)
            .annotate(already_reviewed=Exists(user_review_exists))
            .select_related("user")
        )

        reviews = Review.objects.filter(
            Q(user_id__in=allowed_user_ids) | Q(ticket__user=self.request.user)
        ).select_related(
            "user",
            "ticket",
            "ticket__user",
        )

        # Mix and sort by creation datetime (descending)
        posts = sorted(
            chain(tickets, reviews),
            key=lambda obj: obj.time_created,
            reverse=True,
        )

        context["posts"] = posts
        return context
