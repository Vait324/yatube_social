from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.group = Group.objects.create(
                title='Тестовый заголовок',
                slug='test_slug',
        )
        posts = []
        for i in range(1, 14):
            posts.append(Post(
                text='text' + str(i),
                author=cls.user,
                group=cls.group
            ))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        """Первая страница содержит 10 записей из 13"""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """Вторая стрница содержит 3 записи из 13"""
        response = self.authorized_client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
