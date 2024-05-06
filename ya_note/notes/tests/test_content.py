from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Александр Пушкин')
        cls.reader = User.objects.create(username='Евгений Онегин')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)

    def test_pages_contains_form(self):
        """Тест проверяет наличие формы для создания заметки"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_note_not_in_list_for_another_user(self):
        """Тест проверяет наличие заметки для разных пользователей"""
        urls = (
            (self.auth_client, True),
            (self.auth_reader, False)
        )
        for user_status, note_in_list in urls:
            with self.subTest(
                user_status=user_status,
                note_in_list=note_in_list
            ):
                url = reverse('notes:list')
                response = user_status.get(url)
                object_list = response.context.get('object_list')
                self.assertEqual((self.note in object_list), note_in_list)
