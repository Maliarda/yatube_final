from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для тестирования тестового поста",
        )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name_for_post_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "author": "Автор",
            "group": "Группа",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_for_post_model(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "group": "Группа, к которой будет относиться пост",
            "text": "Введите текст поста",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name_for_group_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            "title": "Название группы",
            "description": "Описание группы",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_for_group_model(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            "title": "Введите название группы",
            "description": "Опишите о чем эта группа",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthor")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост для тестирования тестового комментария",
        )
        cls.comment = Comment.objects.create(
            author=cls.user, text="Тестовый комментарий", post=cls.post
        )

    def setUp(self):
        self.user = User.objects.create_user(username="SneakyFox")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_model_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

    def test_verbose_name_for_comment_model(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            "author": "Автор",
            "text": "Текст комментария",
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text_for_comment_model(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            "author": "Автор комментария",
            "text": "Введите текст комментария",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value
                )
