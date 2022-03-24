import shutil
import tempfile
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Заголовок тестовой группы",
            slug="test_slug",
            description="Тестовое описание",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """После отправки валидной формы создается пост,
        происходит переадресация в профиль
        """
        count_posts = Post.objects.count()
        form_data = {"text": "Данные из формы", "group": self.group.id}
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = self.user
        group_1 = self.group
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": "HasNoName"}),
        )
        self.assertEqual(post_1.text, "Данные из формы")
        self.assertEqual(author_1.username, "HasNoName")
        self.assertEqual(group_1.title, "Заголовок тестовой группы")

    def test_edit_post(self):
        """После отправки валидной формы редактирования пост изменяется"""
        form_data = {"text": "Данные из формы", "group": self.group.id}
        self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        form_data = {"text": "Измененный текст", "group": self.group.id}
        response_edit = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": post_2.id},
            ),
            data=form_data,
            follow=True,
        )
        post_2 = Post.objects.get(id=self.group.id)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_2.text, "Измененный текст")

    def test_create_post_for_guest(self):
        """Гость не может создать пост, редирект на login"""
        count_posts = Post.objects.count()
        response = self.guest_client.get(
            reverse("posts:post_create"), follow=True
        )
        self.assertRedirects(
            response,
            (
                reverse("users:login")
                + "?next="
                + urllib.parse.quote(reverse("posts:post_create"), "")
            ),
        )
        self.assertEqual(Post.objects.count(), count_posts)

    def test_post_with_picture(self):
        """Пост создается с картинкой"""
        count_posts = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Пост с картинкой",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        post_1 = Post.objects.get(id=self.group.id)
        author_1 = User.objects.get(username="HasNoName")
        group_1 = Group.objects.get(title="Заголовок тестовой группы")
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": "HasNoName"}),
        )
        self.assertEqual(post_1.text, "Пост с картинкой")
        self.assertEqual(author_1.username, "HasNoName")
        self.assertEqual(group_1.title, "Заголовок тестовой группы")


class CommentCreateFormTests(TestCase):
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
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """После успешной отправки авторизованным пользователем
        комментарий появляется на странице поста."""
        count_comments = self.post.comments.count()
        form_data = {"text": "тестовый комментарий"}
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(self.post.comments.last().text, form_data["text"])
        self.assertEqual(self.post.comments.count(), count_comments + 1)
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id}),
        )
