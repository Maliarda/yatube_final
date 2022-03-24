from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(  # type: ignore
            username="TestAuthor",
            email="test@mail.ru",
            password="test_pass",
        )

    def setUp(self):

        self.guest_client = Client()

        self.user = User.objects.create_user(username="HasNoName")

        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """Во view функциях users используются правильные шаблоны."""
        templates_page_names = {
            "users/signup.html": reverse("users:signup"),
            "users/login.html": reverse("users:login"),
            "users/password_reset_done.html": reverse(
                "users:password_reset_done"
            ),
            "users/password_reset_form.html": reverse("users:password_reset"),
            "users/password_reset_complete.html": reverse(
                "users:password_reset_complete"
            ),
            "users/password_change_form.html": reverse(
                "users:password_change"
            ),
            "users/password_change_done.html": reverse(
                "users:password_change_done"
            ),
            "users/logged_out.html": reverse("users:logout"),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
