from django.test import Client, TestCase
from django.urls.base import reverse

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_error_404(self):
        response = self.guest_client.get('404')
        self.assertEqual(response.status_code, 404)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2 = User.objects.create(username='Andrey')
        cls.user3 = User.objects.create(username='Pavel')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='2021-01-02',
            author=PostsURLTests.user2,
            id=1
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание группы'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostsURLTests.user2
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage_for_anybody(self):
        """Страница / доступна всем"""
        response = self.guest_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_groupage_for_anybody(self):
        """Старница group/slug Доступна всем"""
        response = self.guest_client.get(reverse('group', kwargs={
            'slug': PostsURLTests.group.slug
        }))
        self.assertEqual(response.status_code, 200)

    def test_new_postpage_for_authorized(self):
        """Страница создания поста доступна авторизироавнному пользователю"""
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_new_postpage_for_guest_redirecting(self):
        """Переадресация на регистрацию со страницы создания поста"""
        response = self.guest_client.get(reverse('new_post'), follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' +
                             reverse('new_post'))

    def test_profile_page(self):
        """Страница профиля пользователя"""
        response = self.authorized_client.get(reverse('profile', kwargs={
            'username': PostsURLTests.user2.username
        }))
        self.assertEqual(response.status_code, 200)

    def test_post_page(self):
        """Страница поста"""
        response = self.authorized_client.get(reverse('post', kwargs={
            'username': PostsURLTests.user2.username,
            'post_id': PostsURLTests.post.pk
        }))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_page(self):
        """Страница редактирования поста"""
        response = self.authorized_client.get(reverse('post_edit', kwargs={
            'username': PostsURLTests.user2.username,
            'post_id': PostsURLTests.post.pk
        }))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_page_redirect(self):
        """Переадресация на регистрацию не авторизированного пользователя
         со страницы редактирования поста"""
        original_url = reverse('post_edit', kwargs={
            'username': PostsURLTests.user2.username,
            'post_id': PostsURLTests.post.pk
        })
        response = self.guest_client.get(original_url, follow=True)
        self.assertRedirects(response, reverse('login') + '?next=' +
                             original_url)

    def test_post_edit_page_wrong_author(self):
        """Переадресация на регистрацию при попытке
         отредактировать чужой пост"""
        original_url = reverse('post_edit', kwargs={
            'username': PostsURLTests.user3.username,
            'post_id': PostsURLTests.post.pk
        })
        response = self.guest_client.get(original_url, follow=True)
        self.assertRedirects(response,  reverse('login') + '?next=' +
                             original_url)

    def test_url_uses_correct_templates(self):
        """URL используют соответствующие шаблоны"""
        templates_url_names = {
            reverse('index'): 'index.html',
            reverse('group',
                    kwargs={'slug': PostsURLTests.group.slug}): 'group.html',
            reverse('new_post'): 'posts/new.html',
            reverse('profile',
                    kwargs={'username': PostsURLTests.user2}): 'profile.html',
            reverse('post_edit', kwargs={
                'username': PostsURLTests.user2,
                'post_id': PostsURLTests.post.pk}): 'posts/new.html',
            reverse('post', kwargs={
                'username': PostsURLTests.user2,
                'post_id': PostsURLTests.post.pk}): 'post.html',
            reverse('500'): 'misc/500.html',
            reverse('404'): 'misc/404.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_guest_redirect_from_adding_comment(self):
        """Переадресация не авторизированного пользователя на
        регистрацию при попытке добавить комментарий"""
        original_url = reverse('add_comment', kwargs={
            'username': PostsURLTests.user2.username,
            'post_id': PostsURLTests.post.pk
        })
        response = self.guest_client.get(original_url, follow=True)
        self.assertRedirects(response,  reverse('login') + '?next=' +
                             original_url)

    def test_subscribe_to_author(self):
        """Проверка возможности подписаться на автора"""
        # Напишу тест после ревью. К сожалению, пока не успеваю

    def test_unsubscrube_from_author(self):
        """Проверка возможности отписаться от автора"""
        # Напишу тест после ревью. К сожалению, пока не успеваю

    def test_new_post_in_required_follow_page(self):
        """Новый пост отображается на странице соответствующего подписчика"""
        # Напишу тест после ревью. К сожалению, пока не успеваю
