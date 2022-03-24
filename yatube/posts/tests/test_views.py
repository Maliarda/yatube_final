import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
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

        cls.post = Post.objects.create(
            text="Тестовый текст 2",
            author=User.objects.create_user(
                username="TestAuthor2",
                email="test2@mail.ru",
                password="test_pass",
            ),
            group=Group.objects.create(
                title="Тестовая группа 2", slug="test_slug2"
            ),
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_pages_use_correct_template(self):
        """Во view функциях posts используются правильные шаблоны."""
        templates_page_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test_slug"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "TestAuthor"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": "1"}
            ): "posts/post_detail.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": "2",
                },
            ): "posts/create_post.html",
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        first_object_dict = {
            first_object.text: "Тестовый текст 2",
            first_object.author.username: "TestAuthor2",
            first_object.group.title: "Тестовая группа 2",
            first_object.image: "posts/small.gif",
        }
        for received, expected in first_object_dict.items():
            with self.subTest(received=received):
                self.assertEqual(received, expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон страницы поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": "2"})
        )
        first_object = response.context["post"]
        first_object_dict = {
            first_object.text: "Тестовый текст 2",
            first_object.author.username: "TestAuthor2",
            first_object.group.title: "Тестовая группа 2",
            first_object.image: "posts/small.gif",
        }
        for received, expected in first_object_dict.items():
            with self.subTest(received=received):
                self.assertEqual(received, expected)

    def test_group_list_show_correct_context(self):
        """Шаблон группы сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_slug2"})
        )
        first_object = response.context["group"]
        first_object_dict = {
            first_object.title: "Тестовая группа 2",
            first_object.slug: "test_slug2",
            Post.objects.first().image: "posts/small.gif",
        }
        for received, expected in first_object_dict.items():
            with self.subTest(received=received):
                self.assertEqual(received, expected)

    def test_profile_correct_context(self):
        """Шаблон профиля сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse("posts:profile", kwargs={"username": "TestAuthor2"})
        )
        first_object = response.context["page_obj"][0]
        first_object_dict = {
            first_object.text: "Тестовый текст 2",
            response.context["author"].username: "TestAuthor2",
            first_object.image: "posts/small.gif",
        }
        for received, expected in first_object_dict.items():
            with self.subTest(received=received):
                self.assertEqual(received, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertNotIn("is_edit", response.context)

    def test_edit_post_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": "2"})
        )
        self.assertIsInstance(response.context.get("form"), PostForm)
        self.assertTrue(response.context["is_edit"])

    def test_post_show_on_template(self):
        """Пост появляется на главной странице, странице выбранной группы и
        профиля пользователя."""
        urls_tuple = {
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test_slug2"}),
            reverse("posts:profile", kwargs={"username": "TestAuthor2"}),
        }
        for url in urls_tuple:
            response = self.client.get(url)
            self.assertIn(self.post, response.context["page_obj"].object_list)

    def test_post_another_group(self):
        """Пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse("posts:group_list", kwargs={"slug": "test_slug"})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, "Тестовый текст 2")


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username="TestAuthor",
            email="test@mail.ru",
            password="test_pass",
        )
        cls.group = Group.objects.create(
            title=("Тестовая группа"),
            slug="test_slug",
            description="Тестовое описание",
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(
                Post(
                    text=f"Тестовый пост {i}",
                    author=cls.author,
                    group=cls.group,
                )
            )

        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        """На главной, странице групп и профиля выводится 10 постов"""
        urls_tuple = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test_slug"}),
            reverse("posts:profile", kwargs={"username": "TestAuthor"}),
        )
        for tested_url in urls_tuple:
            response = self.client.get(tested_url)
            self.assertEqual(response.context["page_obj"].end_index(), 10)

    def test_second_page_contains_three_posts(self):
        """Пагинатор корректно разделяет более 10 постов"""
        urls_tuple = (
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test_slug"}),
            reverse("posts:profile", kwargs={"username": "TestAuthor"}),
        )
        for url in urls_tuple:
            response = self.client.get(url + "?page=2")
            self.assertEqual(response.context["page_obj"].end_index(), 13)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username="TestAuthor",
                email="test@mail.ru",
                password="test_pass",
            ),
            text="Тестовая запись для создания поста",
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест кэширования страницы index.html"""
        first_state = self.authorized_client.get(reverse("posts:index"))
        post_1 = Post.objects.get(id=1)
        post_1.text = "Измененный текст"
        post_1.save()
        second_state = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(first_state.content, second_state.content)
        cache.clear()
        third_state = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(first_state.content, third_state.content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(
            username="follower", email="follower@mail.ru", password="test_pass"
        )
        self.user_following = User.objects.create_user(
            username="following",
            email="following@mail.ru",
            password="test_pass",
        )
        self.post = Post.objects.create(
            author=self.user_following,
            text="Тестовая запись для тестирования ленты",
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей"""
        self.client_auth_follower.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_following.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """Авторизованный пользователь может удалить
        подписку на других пользователей"""
        self.client_auth_follower.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.user_following.username},
            )
        )
        self.client_auth_follower.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.user_following.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        Follow.objects.create(
            user=self.user_follower, author=self.user_following
        )
        response = self.client_auth_follower.get("/follow/")
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual(post_text_0, "Тестовая запись для тестирования ленты")
        response = self.client_auth_following.get("/follow/")
        self.assertNotContains(
            response, "Тестовая запись для тестирования ленты"
        )
