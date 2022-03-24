from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="TestAuthor",
            email="test@mail.ru",
            password="test_pass",
        )

    def setUp(self):

        self.guest_client = Client()

        self.user = User.objects.create_user(username="HasNoName")

        self.authorized_client = Client()

        self.authorized_client.force_login(self.user)

    def test_singup_login_password_reset(self):
        """Страницы авторизации, регистрации, сброса пароля доступны всем"""
        url_names = (
            "/auth/signup/",
            "/auth/login/",
            "/auth/reset/<uidb64>/<token>/",
            "/auth/password_reset/done/",
            "/auth/password_reset/",
            "/auth/reset/done/",
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout_password_change(self):
        """Выход, смены пароля доступны авторизованным пользователям"""
        url_names = (
            "/auth/password_change/",
            "/auth/password_change/done/",
            "/auth/logout/",
        )
        for address in url_names:
            with self.subTest():
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_template_for_users(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/auth/signup/": "users/signup.html",
            "/auth/login/": "users/login.html",
            ("/auth/reset/<uidb64>/<token>/"): (
                "users/password_reset_confirm.html"
            ),
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/password_reset/": "users/password_reset_form.html",
            "/auth/reset/done/": "users/password_reset_complete.html",
            "/auth/password_change/": "users/password_change_form.html",
            "/auth/password_change/done/": "users/password_change_done.html",
            "/auth/logout/": "users/logged_out.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
