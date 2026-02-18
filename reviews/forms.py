from django import forms

from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    """
    Form used to create or update a Ticket.
    The 'user' and 'time_created' fields are set automatically.
    """
    class Meta:
        model = Ticket
        fields = ("title", "description", "image")
        widgets = {
            "title": forms.TextInput(attrs={"autocomplete": "off"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }


class ReviewForm(forms.ModelForm):
    """
    Form used to create or update a Review.
    The 'user', 'ticket' and 'time_created' fields are set automatically.
    """
    class Meta:
        model = Review
        fields = ("rating", "headline", "body")
        widgets = {
            "headline": forms.TextInput(attrs={"autocomplete": "off"}),
            "body": forms.Textarea(attrs={"rows": 7}),
        }


class FollowUserForm(forms.Form):
    """
    Simple form to follow a user by their username.
    """
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={"autocomplete": "off"})
    )