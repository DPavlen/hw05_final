import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_new_record_in_DB(self):
        """при отправке валидной формы со страницы создания поста
        reverse('posts:create_post') создаётся новая запись в базе данны"""
        form_data = {
            'text': 'Данные из формы',
            'group': self.group.pk,
        }
        count_posts = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(Post.objects.filter(
                        text=form_data.get('text'),
                        group=form_data.get('group'),
                        author=self.user
                        ).exists())
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'author'}))

    def test_edit_post_authorized_client(self):
        """При отправке валидной формы со страницы редактирования поста
        reverse('posts:post_edit', args=('post_id',))
        происходит изменение поста с post_id в базе данных."""
        form_data = {
            'text': 'Измененный текст поста',
            'group': self.group.pk,
        }
        response_edit_post = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                    'post_id': self.post.pk
                    }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(id=self.post.pk)
        self.assertEqual(response_edit_post.status_code, HTTPStatus.OK)
        self.assertEqual(post_edit.text, form_data.get('text'))
        self.assertEqual(post_edit.group.pk, form_data.get('group'))

    def test_create_post_not_authorized(self):
        """Неавторизованный клиент и проверить с ним создание."""
        form_data = {
            'text': 'Текст',
            'group': 'Группа'
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
                         text='Текст'
                         ).exists())

    def test_post_edit_not_authorized(self):
        """Неавторизованный клиент и проверить с ним редактирование."""
        form_data = {
            'text': 'Текст',
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.group.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        posts_count = Post.objects.count()
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
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': f'{self.user.username}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
