from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Ticket(models.Model):
    """
    A Ticket is a request for a review (book or article).
    It can optionally include an image.
    """

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)

    # The author of the ticket
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    # Optional image (requires Pillow)
    image = models.ImageField(null=True, blank=True, upload_to="tickets/")

    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # Display a helpful label in the Django admin
        return self.title


class Review(models.Model):
    """
    A Review is linked to a Ticket and written by a user.
    Rating must be between 0 and 5.
    """

    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192, blank=True)

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        # Show the ticket and headline for clarity
        return f"{self.ticket.title} - {self.headline}"


class UserFollows(models.Model):
    """
    User relationship table: 'user follows followed_user'.
    """

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )

    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_by",
    )

    class Meta:
        # Prevent duplicate follow relationships
        unique_together = ("user", "followed_user")

    def __str__(self) -> str:
        return f"{self.user} -> {self.followed_user}"