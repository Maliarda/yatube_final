from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=User.objects.create_user(
                username="TestAuthor",
                email="test@mail.ru",
                password="test_pass",
            ),
            group=Group.objects.create(
                title="Тестовая группа", slug="test_slug"
            ),
        )

    def setUp(self):

        self.guest_client = Client()

        self.user = User.objects.create_user(username="HasNoName")

        self.authorized_client = Client()

        self.authorized_client.force_login(self.post.author)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user)

    def test_home_and_group(self):
        """Главная,страницы групп, профиля и поста доступны всем"""
        url_names = (
            "/",
            "/group/test_slug/",
            "/profile/TestAuthor/",
            "/posts/1/",
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница создания записи доступна авторизованному пользователю."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_for_author(self):
        """Страница редактирования записи доступна только автору."""
        response = self.authorized_client.get("/posts/1/edit")
        self.assertEqual(response.status_code, HTTPStatus.MOVED_PERMANENTLY)

    def test_edit_redirect_guest_on_login(self):
        """Попытка редактирования перенаправит анонимного
        пользователя на страницу авторизации."""
        response = self.guest_client.get("/posts/1/edit/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/posts/1/edit/")

    def test_edit_redirect_autorized_not_author_on_post_detail(self):
        """Попытка редактирования не автором перенаправит
        пользователя на страницу поста."""
        response = self.authorized_client_not_author.get(
            "/posts/1/edit/", follow=True
        )
        self.assertRedirects(response, "/posts/1/")

    def test_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test_slug/": "posts/group_list.html",
            "/profile/TestAuthor/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """ошибке 404 отработает view-функция
        и отобразится кастомная страница ошибки"""
        response = self.guest_client.get("/John_Doe_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")

    def test_add_comment_redirect_guest_on_login(self):
        """Попытка комментирования переведет анонимного
        пользователя на страницу авторизации."""
        response = self.guest_client.get("/posts/1/comment/", follow=True)
        self.assertRedirects(response, "/auth/login/?next=/posts/1/comment/")
