from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Review, Ticket, UserFollows


User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password")
        self.ticket = Ticket.objects.create(title="Livre", user=self.user)

    def test_rating_accepts_values_between_zero_and_five(self):
        for rating in (0, 5):
            review = Review(
                ticket=self.ticket,
                rating=rating,
                headline=f"Note {rating}",
                user=self.user,
            )
            review.full_clean()

    def test_rating_rejects_values_outside_allowed_range(self):
        for rating in (-1, 6):
            review = Review(
                ticket=self.ticket,
                rating=rating,
                headline=f"Note {rating}",
                user=self.user,
            )
            with self.assertRaises(ValidationError):
                review.full_clean()

    def test_follow_relationship_cannot_be_duplicated(self):
        followed = User.objects.create_user(username="bob", password="password")
        UserFollows.objects.create(user=self.user, followed_user=followed)

        with self.assertRaises(IntegrityError):
            UserFollows.objects.create(user=self.user, followed_user=followed)


class TicketViewsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="alice", password="password")
        self.other_user = User.objects.create_user(username="bob", password="password")
        self.client.force_login(self.owner)

    def test_create_ticket_assigns_authenticated_user(self):
        response = self.client.post(
            reverse("ticket_create"),
            {"title": "Dune", "description": "Votre avis ?"},
        )

        self.assertRedirects(response, reverse("posts"))
        self.assertTrue(Ticket.objects.filter(title="Dune", user=self.owner).exists())

    def test_only_owner_can_update_ticket(self):
        ticket = Ticket.objects.create(title="Dune", user=self.owner)
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("ticket_edit", args=[ticket.pk]),
            {"title": "Titre modifié", "description": "Description"},
        )

        self.assertEqual(response.status_code, 403)
        ticket.refresh_from_db()
        self.assertEqual(ticket.title, "Dune")

    def test_only_owner_can_delete_ticket(self):
        ticket = Ticket.objects.create(title="Dune", user=self.owner)
        self.client.force_login(self.other_user)

        response = self.client.post(reverse("ticket_delete", args=[ticket.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ticket.objects.filter(pk=ticket.pk).exists())


class ReviewViewsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="alice", password="password")
        self.other_user = User.objects.create_user(username="bob", password="password")
        self.ticket = Ticket.objects.create(title="Dune", user=self.other_user)
        self.client.force_login(self.author)

    def test_create_review_assigns_user_and_ticket(self):
        response = self.client.post(
            reverse("review_create", args=[self.ticket.pk]),
            {"headline": "Excellent", "rating": 5, "body": "Très bon livre."},
        )

        self.assertRedirects(response, reverse("posts"))
        self.assertTrue(
            Review.objects.filter(user=self.author, ticket=self.ticket, rating=5).exists()
        )

    def test_duplicate_review_is_refused(self):
        Review.objects.create(
            user=self.author,
            ticket=self.ticket,
            headline="Première critique",
            rating=4,
        )

        response = self.client.post(
            reverse("review_create", args=[self.ticket.pk]),
            {"headline": "Deuxième critique", "rating": 5, "body": "Doublon"},
        )

        self.assertRedirects(response, reverse("feed"))
        self.assertEqual(Review.objects.filter(user=self.author, ticket=self.ticket).count(), 1)

    def test_only_owner_can_update_review(self):
        review = Review.objects.create(
            user=self.author,
            ticket=self.ticket,
            headline="Avis",
            rating=4,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse("review_edit", args=[review.pk]),
            {"headline": "Modification", "rating": 1, "body": "Non autorisée"},
        )

        self.assertEqual(response.status_code, 403)
        review.refresh_from_db()
        self.assertEqual(review.headline, "Avis")

    def test_only_owner_can_delete_review(self):
        review = Review.objects.create(
            user=self.author,
            ticket=self.ticket,
            headline="Avis",
            rating=4,
        )
        self.client.force_login(self.other_user)

        response = self.client.post(reverse("review_delete", args=[review.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(pk=review.pk).exists())


class FollowViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password")
        self.followed = User.objects.create_user(username="bob", password="password")
        self.third_user = User.objects.create_user(username="charlie", password="password")
        self.client.force_login(self.user)

    def test_following_user_is_idempotent(self):
        url = reverse("follow_add")

        self.client.post(url, {"username": self.followed.username})
        self.client.post(url, {"username": self.followed.username})

        self.assertEqual(
            UserFollows.objects.filter(user=self.user, followed_user=self.followed).count(),
            1,
        )

    def test_user_cannot_follow_themself(self):
        response = self.client.post(reverse("follow_add"), {"username": self.user.username})

        self.assertRedirects(response, reverse("follow_list"))
        self.assertFalse(UserFollows.objects.filter(user=self.user).exists())

    def test_unknown_username_is_refused(self):
        response = self.client.post(reverse("follow_add"), {"username": "inconnu"})

        self.assertRedirects(response, reverse("follow_list"))
        self.assertFalse(UserFollows.objects.filter(user=self.user).exists())

    def test_user_cannot_remove_another_users_relationship(self):
        relation = UserFollows.objects.create(
            user=self.third_user,
            followed_user=self.followed,
        )

        response = self.client.post(reverse("follow_remove", args=[relation.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(UserFollows.objects.filter(pk=relation.pk).exists())


class TicketReviewCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password")
        self.client.force_login(self.user)
        self.url = reverse("review_create_ticket")
        self.valid_data = {
            "title": "Dune",
            "description": "Un classique",
            "headline": "Excellent",
            "rating": 5,
            "body": "Une critique.",
        }

    def test_creates_linked_ticket_and_review(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertRedirects(response, reverse("posts"))
        ticket = Ticket.objects.get()
        review = Review.objects.get()
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.ticket, ticket)

    def test_invalid_review_creates_nothing(self):
        invalid_data = {**self.valid_data, "rating": 9}

        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ticket.objects.exists())
        self.assertFalse(Review.objects.exists())

    def test_review_save_failure_rolls_back_ticket(self):
        with patch("reviews.views.Review.save", side_effect=RuntimeError("échec")):
            with self.assertRaises(RuntimeError):
                self.client.post(self.url, self.valid_data)

        self.assertFalse(Ticket.objects.exists())
        self.assertFalse(Review.objects.exists())


class FeedViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password")
        self.followed = User.objects.create_user(username="bob", password="password")
        self.outsider = User.objects.create_user(username="charlie", password="password")
        UserFollows.objects.create(user=self.user, followed_user=self.followed)
        self.client.force_login(self.user)

    def test_feed_includes_expected_content_and_excludes_unrelated_content(self):
        own_ticket = Ticket.objects.create(title="Mon billet", user=self.user)
        followed_ticket = Ticket.objects.create(title="Billet suivi", user=self.followed)
        unrelated_ticket = Ticket.objects.create(title="Billet externe", user=self.outsider)
        response_to_own_ticket = Review.objects.create(
            ticket=own_ticket,
            user=self.outsider,
            headline="Réponse externe",
            rating=4,
        )
        followed_review = Review.objects.create(
            ticket=unrelated_ticket,
            user=self.followed,
            headline="Critique suivie",
            rating=3,
        )
        unrelated_review = Review.objects.create(
            ticket=unrelated_ticket,
            user=self.outsider,
            headline="Critique externe",
            rating=2,
        )

        response = self.client.get(reverse("feed"))
        posts = response.context["posts"]

        self.assertIn(own_ticket, posts)
        self.assertIn(followed_ticket, posts)
        self.assertIn(response_to_own_ticket, posts)
        self.assertIn(followed_review, posts)
        self.assertNotIn(unrelated_ticket, posts)
        self.assertNotIn(unrelated_review, posts)

    def test_feed_is_ordered_from_newest_to_oldest(self):
        older_ticket = Ticket.objects.create(title="Ancien", user=self.user)
        newer_ticket = Ticket.objects.create(title="Récent", user=self.user)
        Ticket.objects.filter(pk=older_ticket.pk).update(
            time_created=timezone.now() - timedelta(days=1)
        )

        response = self.client.get(reverse("feed"))

        self.assertEqual(response.context["posts"][:2], [newer_ticket, older_ticket])

    def test_ticket_is_annotated_when_current_user_has_reviewed_it(self):
        ticket = Ticket.objects.create(title="Billet suivi", user=self.followed)
        Review.objects.create(
            ticket=ticket,
            user=self.user,
            headline="Mon avis",
            rating=5,
        )

        response = self.client.get(reverse("feed"))
        displayed_ticket = next(post for post in response.context["posts"] if isinstance(post, Ticket))

        self.assertTrue(displayed_ticket.already_reviewed)


class PostsViewTests(TestCase):
    def test_posts_page_only_contains_current_users_content(self):
        user = User.objects.create_user(username="alice", password="password")
        other_user = User.objects.create_user(username="bob", password="password")
        own_ticket = Ticket.objects.create(title="Mon billet", user=user)
        other_ticket = Ticket.objects.create(title="Autre billet", user=other_user)
        own_review = Review.objects.create(
            ticket=other_ticket,
            user=user,
            headline="Mon avis",
            rating=4,
        )
        other_review = Review.objects.create(
            ticket=own_ticket,
            user=other_user,
            headline="Autre avis",
            rating=3,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("posts"))

        self.assertQuerySetEqual(response.context["tickets"], [own_ticket])
        self.assertQuerySetEqual(response.context["reviews"], [own_review])
        self.assertNotIn(other_review, response.context["reviews"])

# Create your tests here.
