from django.test import TestCase

from ..models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='Test-slug-field',
            description='Тестовое описание группы'
        )
        cls.group = Group.objects.get(id=1)

    def test_verbose_name(self):
        """Проверка verbose_name модели Group"""
        group = GroupModelTest.group
        field_verbose_name = {
            'title': 'Сообщество',
            'description': 'Описание'
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_name(self):
        """Проверка help_text модели Group"""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Укажите сообщество',
            'description': 'Описание группы'
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_name_as_title(self):
        group = GroupModelTest.group
        expected_name = group.title
        self.assertEqual(expected_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            id=1,
            text='Тестовый текст записи',
            pub_date='2021-01-02',
            author=User.objects.create(username='testuser')
        )
        cls.post = Post.objects.get(id=1)

    def test_verbose_name(self):
        """Проверка verbose_name модели Post"""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст записи',
            'pub_date': 'дата публикации'
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_name(self):
        """Проверка help_text модели Post"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст записи',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_name_as_text(self):
        """Текст поста как предпросмотр"""
        post = PostModelTest.post
        expected_name = post.text[:15]
        self.assertEqual(expected_name, str(post))
