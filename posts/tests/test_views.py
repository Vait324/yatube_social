from django import forms
from django.test import Client, TestCase
from django.urls import reverse
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User, Follow


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user2 = User.objects.create(username='Andrey')
        cls.user3 = User.objects.create(username='Pavel')
        cls.user4 = User.objects.create(username='Ivan')
        cls.group = Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание группы'
        )

        cls.group2 = Group.objects.create(
            id=2,
            title='Тестовая группа2',
            slug='group-slug2',
            description='Тестовое описание группы2'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            id=1,
            text='Тестовый текст',
            pub_date='2021-01-02',
            author=PostPagesTest.user2,
            group=PostPagesTest.group,
            image=uploaded
        )
        cls.follow = Follow.objects.create(
            user=PostPagesTest.user2,
            author=PostPagesTest.user4
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = PostPagesTest.user2
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """View функции использует соответствующие шаблоны"""
        templates_page_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group',
                                  kwargs={'slug': PostPagesTest.group.slug}),
            'posts/new.html': reverse('new_post')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_text_and_image_check(self, context, post):
        """Проверка текста и картинки поста из списка постов"""
        self.assertEqual(context[0].text, post.post.text)
        self.assertEqual(context[0].image, post.post.image)

    def test_index_page_use_correct_context(self):
        """index сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse('index'))
        post_author = response.context.get('page')[0].author.username
        self.post_text_and_image_check(response.context.get('page'),
                                       PostPagesTest)
        self.assertEqual(post_author, str(PostPagesTest.user2))

    def test_group_page_use_correct_context(self):
        """страница сообщества сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostPagesTest.group.slug})
        )
        self.assertEqual(response.context.get('group').title,
                         PostPagesTest.group.title)
        self.assertEqual(response.context.get('group').description,
                         PostPagesTest.group.description)
        self.assertEqual(response.context.get('group').slug,
                         PostPagesTest.group.slug)

    def test_new_post_use_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_in_correct_group(self):
        """Посту присваевается требуемое сообщество"""
        post_in_group1 = Post.objects.filter(
            group__title=PostPagesTest.group.title
            )
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': PostPagesTest.group.slug})
        )
        self.assertIn(response.context['page'][0], post_in_group1)

    def test_profile_use_correct_context(self):
        """Страница пользователся формируется с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': PostPagesTest.user2})
        )
        self.assertEqual(response.context.get('author').username,
                         str(PostPagesTest.user2))
        self.post_text_and_image_check(response.context.get('user_posts'),
                                       PostPagesTest)
        self.assertEqual(len(response.context['user_posts']), 1)

    def test_post_view_use_correct_context(self):
        """Страница поста формируется с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': PostPagesTest.user2.username,
                'post_id': PostPagesTest.post.id
            })
        )
        self.assertEqual(response.context['post_count'], 1)
        self.assertEqual(response.context.get('author').username,
                         str(PostPagesTest.user2))
        self.assertEqual(response.context.get('post').text,
                         PostPagesTest.post.text)
        self.assertEqual(response.context.get('post').image,
                         PostPagesTest.post.image)

    def test_post_edit_use_correct_context(self):
        """Страница редактирования поста формируется с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': PostPagesTest.user2.username,
                'post_id': PostPagesTest.post.id
            })
        )
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('is_edit'), True)

    def test_index_cache(self):
        """ Проверка кэширования главной страницы """
        n1_request = self.guest_client.get(reverse('index'))
        Post.objects.create(id=35, text='Тестовый текст',
                            pub_date='2021-01-02',
                            author=PostPagesTest.user2,)
        n2_request = self.guest_client.get(reverse('index'))
        posts = []
        for i in range(1, 14):
            posts.append(Post(
                text='text' + str(i),
                author=PostPagesTest.user2,
                group=PostPagesTest.group
            ))
        Post.objects.bulk_create(posts)
        n3_request = self.guest_client.get(reverse('index') + '?page=2')
        self.assertHTMLEqual(str(n1_request.content),
                             str(n2_request.content), msg=None)
        self.assertHTMLNotEqual(str(n1_request.content),
                                str(n3_request.content), msg=None)

    def test_subscribe_to_author(self):
        """Проверка возможности подписаться на автора"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_follow', kwargs={
                'username': PostPagesTest.user3.username,
            }))
        self.assertEqual(Follow.objects.count(), follow_count+1)

    def test_unsubscrube_from_author(self):
        """Проверка возможности отписаться от автора"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('profile_unfollow', kwargs={
                'username': PostPagesTest.user4
            }))
        self.assertEqual(Follow.objects.count(), follow_count-1)

    def test_new_post_in_required_follow_page(self):
        """Новый пост отображается на странице подписчика"""
        post_for_sub = Post.objects.create(
            id=44,
            text='For my subs',
            pub_date='2021-01-02',
            author=PostPagesTest.user4
        )
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(response.context.get('post').text,
                         post_for_sub.text)
