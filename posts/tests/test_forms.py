import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user2 = User.objects.create(username='Andrey')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=PostFormTest.user2,
            id=1
        )
        cls.group = Group.objects.create(slug='test-group')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = PostFormTest.user2
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка функции создания нового поста."""
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст поста',
            'group': PostFormTest.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse('index'))

    def test_edit_post(self):
        """Проверка функции редактирования поста."""
        form_data = {'text': 'Измененный текст поста'}
        response = self.authorized_client.post(reverse('post_edit', kwargs={
                'username': PostFormTest.user2.username,
                'post_id': PostFormTest.post.id
            }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('post', kwargs={
            'username': PostFormTest.post.author,
            'post_id': PostFormTest.post.id
        }))
        self.assertEqual(Post.objects.get(id=1).text, form_data['text'])


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user2 = User.objects.create(username='Andrey')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=CommentFormTest.user2,
            id=1,
        )
        cls.comment = Comment.objects.create(
            post=CommentFormTest.post,
            author=CommentFormTest.user2,
            text='Test comment'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = CommentFormTest.user2
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Проверка функции добавления комментария"""
        comment_count = Comment.objects.count()
        reverse_args = {
            'username': CommentFormTest.user2.username,
            'post_id': CommentFormTest.post.pk
        }
        form_data = {
            'post': CommentFormTest.post,
            'author': self.user,
            'text': 'Test comment N2'
        }
        response = self.authorized_client.post(
            reverse('add_comment', kwargs=reverse_args),
            data=form_data, follow=True)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse('post', kwargs=reverse_args))
