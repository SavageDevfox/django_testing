from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()
TITLE = 'Заголовок'
TEXT = 'Текст'
SLUG = 'zagolovok'
TITLE_EDIT = 'Исправленный заголовок'
TEXT_EDIT = 'Исправленный текст'
SLUG_EDIT = 'new_slug'


class TestLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.create_form_data = {
            'title': TITLE,
            'text': TEXT,
            'author': cls.author,
            'slug': SLUG
        }
        cls.edit_form_data = {
            'title': TITLE_EDIT,
            'text': TEXT_EDIT,
            'author': cls.author,
            'slug': SLUG_EDIT
        }
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title=TITLE,
            text=TEXT,
            author=cls.author,
            slug='slug'
        )
        cls.args = (cls.note.slug,)

    def test_authorized_user_add_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.create_form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        note = Note.objects.get(id=2)
        self.assertEqual(notes_count, 2)
        self.assertEqual(note.title, TITLE)
        self.assertEqual(note.text, TEXT)
        self.assertEqual(note.slug, SLUG)

    def test_anonymous_user_add_note(self):
        login_url = reverse('users:login')
        url = reverse('notes:add')
        response = self.client.get(url)
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_create_note_with_same_slug(self):
        Note.objects.create(**self.create_form_data)
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data={
            'title': '-',
            'text': '-',
            'author': self.author,
            'slug': SLUG
        })
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)

    def test_create_note_with_no_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        self.client.post(url, data={
            'title': TITLE,
            'text': TEXT,
            'author': self.author
        })
        slug_in_note = Note.objects.get(id=2).slug
        self.assertEqual(slug_in_note, slugify(SLUG))

    def test_edit_for_different_users(self):
        users_statuses = (
            (self.reader, False),
            (self.author, True)
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                url = reverse('notes:edit', args=(self.note.slug,))
                self.client.post(url, data=self.edit_form_data)
                self.note.refresh_from_db()
                if status:
                    self.assertEqual(self.note.text, TEXT_EDIT)
                else:
                    self.assertEqual(self.note.text, TEXT)

    def test_delete_note(self):
        users_statuses = (
            (self.reader, 1),
            (self.author, 0)
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                url = reverse('notes:delete', args=self.args)
                self.client.post(url)
                note_count = Note.objects.count()
                self.assertEqual(note_count, status)
