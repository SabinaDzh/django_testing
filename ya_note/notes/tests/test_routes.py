from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


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
        cls.author_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client.force_login(cls.author)

        cls.URL_NOTES_HOME = reverse('notes:home')
        cls.URL_NOTES_LIST = reverse('notes:list')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_SUCCESS = reverse('notes:success')
        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_USERS_LOGOUT = reverse('users:logout')
        cls.URL_USERS_SIGNUP = reverse('users:signup')
        cls.URL_NOTES_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTES_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URL_NOTES_DETAIL = reverse('notes:detail', args=(cls.note.slug,))

    def test_pages_availability_for_anonymous_user(self):
        """Тест проверяет доступность страниц анонимным пользователям"""
        urls = (
            self.URL_NOTES_HOME,
            self.URL_USERS_LOGIN,
            self.URL_USERS_LOGOUT,
            self.URL_USERS_SIGNUP,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_availability_pages(self):
        """Тест проверяет доступность страниц авторизованным пользователям"""
        urls = (
            self.URL_NOTES_LIST,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Тест проверяет доступность страниц для
        авторизованных и анонимных пользователей
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )

        urls = (
            self.URL_NOTES_DETAIL,
            self.URL_NOTES_EDIT,
            self.URL_NOTES_DELETE,
        )

        for client, status in users_statuses:
            for url in urls:
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Тест проверяет редирект для анонимных пользователей"""
        login_url = self.URL_USERS_LOGIN
        urls = (
            self.URL_NOTES_DETAIL,
            self.URL_NOTES_EDIT,
            self.URL_NOTES_DELETE,
            self.URL_NOTES_ADD,
            self.URL_NOTES_SUCCESS,
            self.URL_NOTES_LIST
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
