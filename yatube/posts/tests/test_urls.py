from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestAuthorPost")
        cls.user_not_author_post = User.objects.create_user(
            username="TestNotAuthorPost")

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое Описание группы",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая запись поста",
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_user_not_author_post = Client()
        self.authorized_client_user_not_author_post.force_login(
            self.user_not_author_post)

    def test_guest_urls_access(self):
        """Страницы видны всем пользователям."""
        url_names = {
            "/",
            "/group/test-slug/",
            "/profile/TestAuthorPost/",
            f"/posts/{self.post.pk}/",
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_urls_access(self):
        """Страницы видны только авторизованному пользователю."""
        url_names = {
            "",
            "/group/test-slug/",
            "/profile/TestAuthorPost/",
            f"/posts/{self.post.pk}/",
            f"/posts/{self.post.pk}/edit/",
            "/create/"
        }
        for address in url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_redirect_not_author(self):
        """Редирект, при попытке редактирования поста НЕ автором поста.
        """
        response = self.authorized_client_user_not_author_post.get(
            f"/posts/{self.post.pk}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{self.post.pk}/")

    def test_post_edit_redirect_guest_client(self):
        """У анонимного пользователя должен проверяться редирект."""
        response = self.guest_client.\
            get(reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, ('/auth/login/?next=/posts/1/edit/'))

    def test_post_edit_redirect_no_auth_redirect(self):
        """у авторизованного пользователя — не автора поста
        должен проверяться редирект."""
        response = self.authorized_client_user_not_author_post.\
            get(reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))

    def test_url_corret_templates(self):
        """Проверка вызываемых шаблонов для каждого URL-адреса.
        Страницы доступные авторизованному пользователю."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/TestAuthorPost/": "posts/profile.html",
            f"/posts/{self.post.pk}/": "posts/post_detail.html",
            f"/posts/{self.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html"
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_page_not_found(self):
        """Страница несуществующая."""
        response = self.guest_client.get("/unexisiting_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
