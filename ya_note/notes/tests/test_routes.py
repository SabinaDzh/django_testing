from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

URL = {
    'home': reverse('notes:home'),
    'list': reverse('notes:list'),
    'add': reverse('notes:add'),
    'success': reverse('notes:success'),
    'login': reverse('users:login'),
    'logout': reverse('users:logout'),
    'signup': reverse('users:signup'),
    'edit': reverse('notes:edit', args=('note-slug',)),
    'delete': reverse('notes:delete', args=('note-slug',)),
    'detail': reverse('notes:detail', args=('note-slug',))
}


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Александр Пушкин')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )
        cls.user = User.objects.create(username='Евгений Онегин')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_pages_availability_for_anonymous_user(self):
        """Тест проверяет доступность страниц анонимным пользователям"""
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_availability_pages(self):
        """Тест проверяет доступность страниц авторизованным пользователям"""
        urls = (
            ('notes:list'),
            ('notes:add'),
            ('notes:success')
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Тест проверяет доступность страниц для
        авторизованных и анонимных пользователей
        """
        users_statuses = (
            (URL['list'], self.reader_client, HTTPStatus.OK),
            (URL['success'], self.reader_client, HTTPStatus.OK),
            (URL['add'], self.reader_client, HTTPStatus.OK),
            (URL['detail'], self.reader_client, HTTPStatus.NOT_FOUND),
            (URL['edit'], self.reader_client, HTTPStatus.NOT_FOUND),
            (URL['delete'], self.reader_client, HTTPStatus.NOT_FOUND),
            (URL['home'], self.client, HTTPStatus.OK),
            (URL['login'], self.client, HTTPStatus.OK),
            (URL['logout'], self.client, HTTPStatus.OK),
            (URL['signup'], self.client, HTTPStatus.OK),
        )

        for name, client, status in users_statuses:
            with self.subTest(name=name):
                url = name
                response = client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест проверяет редирект для анонимных пользователей"""
        login_url = reverse('users:login')
        urls = (
            (URL['detail']),
            (URL['edit']),
            (URL['delete']),
            (URL['add']),
            (URL['success']),
            (URL['list'])
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
