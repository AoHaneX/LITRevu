from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AuthenticationViewsTests(TestCase):
    def test_home_displays_login_form_for_anonymous_user(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/home.html")

    def test_signup_creates_and_authenticates_user(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "A-strong-password-2026",
                "password2": "A-strong-password-2026",
            },
        )

        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username="alice").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="alice").pk)

    def test_authenticated_home_redirects_to_posts(self):
        user = User.objects.create_user(username="alice", password="password")
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("posts"), fetch_redirect_response=False)

    def test_protected_page_redirects_anonymous_user_to_login(self):
        response = self.client.get(reverse("posts"))

        expected_url = f'{reverse("login")}?next={reverse("posts")}'
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

# Create your tests here.
