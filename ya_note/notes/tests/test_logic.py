from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase

from .service import BaseTestClass
from notes.models import Note

User = get_user_model()


class TestLogic(BaseTestClass, TestCase):
    TITLE_EDIT = 'Исправленный заголовок'
    TEXT_EDIT = 'Исправленный текст'
    SLUG_EDIT = 'new_slug'
    SLUG_CREATE = 'slug'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.create_form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'author': cls.author,
            'slug': cls.SLUG_CREATE
        }
        cls.edit_form_data = {
            'title': cls.TITLE_EDIT,
            'text': cls.TEXT_EDIT,
            'author': cls.author,
            'slug': cls.SLUG_EDIT
        }

    def test_authorized_user_add_note(self):
        self.client.force_login(self.author)
        Note.objects.all().delete()
        url = self.add_url
        response = self.client.post(url, data=self.create_form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        note = Note.objects.get()
        self.assertEqual(notes_count, 1)
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.create_form_data['slug'])

    def test_anonymous_user_add_note(self):
        login_url = self.login_url
        url = self.add_url
        response = self.client.get(url)
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_create_note_with_same_slug(self):
        self.client.force_login(self.author)
        url = self.add_url
        self.client.post(url, data={
            'title': '-',
            'text': '-',
            'author': self.author,
            'slug': self.SLUG
        })
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_create_note_with_no_slug(self):
        self.client.force_login(self.author)
        url = self.add_url
        self.client.post(url, data={
            'title': self.TITLE,
            'text': self.TEXT,
            'author': self.author
        })
        slug_in_note = Note.objects.get().slug
        self.assertEqual(slug_in_note, slugify(self.TITLE))

    def test_edit_for_different_users(self):
        users_statuses = (
            (self.reader, False),
            (self.author, True)
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                url = self.edit_url
                self.client.post(url, data=self.edit_form_data)
                self.note.refresh_from_db()
                if status:
                    self.assertEqual(self.note.text, self.TEXT_EDIT)
                else:
                    self.assertEqual(self.note.text, self.TEXT)

    def test_delete_note(self):
        users_statuses = (
            (self.reader, 1),
            (self.author, 0)
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                url = self.delete_url
                self.client.post(url)
                note_count = Note.objects.count()
                self.assertEqual(note_count, status)
