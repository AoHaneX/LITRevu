from django.contrib import admin

from .models import Ticket, Review, UserFollows


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin configuration for Ticket to make testing easier.
    """
    list_display = ("id", "title", "user", "time_created")
    list_filter = ("time_created", "user")
    search_fields = ("title", "description", "user__username")
    autocomplete_fields = ("user",)
    ordering = ("-time_created",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review to make testing easier.
    """
    list_display = ("id", "ticket", "rating", "headline", "user", "time_created")
    list_filter = ("rating", "time_created", "user")
    search_fields = ("headline", "body", "ticket__title", "user__username")
    autocomplete_fields = ("ticket", "user")
    ordering = ("-time_created",)


@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserFollows to make testing easier.
    """
    list_display = ("id", "user", "followed_user")
    list_filter = ("user", "followed_user")
    search_fields = ("user__username", "followed_user__username")
    autocomplete_fields = ("user", "followed_user")