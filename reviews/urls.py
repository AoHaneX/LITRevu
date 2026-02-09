from django.urls import path

from .views import (
    TicketListView,
    TicketCreateView, TicketUpdateView, TicketDeleteView,
    ReviewCreateView, ReviewUpdateView, ReviewDeleteView,
)

urlpatterns = [
    # Tickets (posts)
    path("ticket/create/", TicketCreateView.as_view(), name="ticket_create"),
    path("ticket/<int:pk>/edit/", TicketUpdateView.as_view(), name="ticket_edit"),
    path("ticket/<int:pk>/delete/", TicketDeleteView.as_view(), name="ticket_delete"),

    # Reviews
    path("review/create/<int:ticket_id>/", ReviewCreateView.as_view(), name="review_create"),
    path("review/<int:pk>/edit/", ReviewUpdateView.as_view(), name="review_edit"),
    path("review/<int:pk>/delete/", ReviewDeleteView.as_view(), name="review_delete"),
    path("ticket/", TicketListView.as_view(), name="ticket_list"),
]