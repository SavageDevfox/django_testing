from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase

from .service import BaseTestClass
from notes.forms import WARNING
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
        Note.objects.all().delete()
        url = self.add_url
        response = self.author_client.post(url, data=self.create_form_data)
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
        expected_num_of_comments = Note.objects.count()
        url = self.add_url
        self.create_form_data['slug'] = self.SLUG
        response = self.author_client.post(url, data=self.create_form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, expected_num_of_comments)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.SLUG + WARNING))

    def test_create_note_with_no_slug(self):
        url = self.add_url
        del self.create_form_data['slug']
        self.author_client.post(url, data=self.create_form_data)
        slug_in_note = Note.objects.get().slug
        self.assertEqual(slug_in_note, slugify(self.TITLE))

    def test_edit_for_author(self):
        url = self.edit_url
        self.author_client.post(url, self.edit_form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.edit_form_data['title'])
        self.assertEqual(self.note.text, self.edit_form_data['text'])
        self.assertEqual(self.note.slug, self.edit_form_data['slug'])

    def test_edit_for_not_author(self):
        note_before_edit = self.note
        url = self.edit_url
        self.reader_client.post(url, self.edit_form_data)
        note_after_edit = Note.objects.get()
        self.assertEqual(note_before_edit.title, note_after_edit.title)
        self.assertEqual(note_before_edit.text, note_after_edit.text)
        self.assertEqual(note_before_edit.slug, note_after_edit.slug)

    def test_delete_note(self):
        users_statuses = (
            (self.reader_client, 1),
            (self.author_client, 0)
        )
        for user, status in users_statuses:
            with self.subTest(user=user):
                url = self.delete_url
                user.post(url)
                note_count = Note.objects.count()
                self.assertEqual(note_count, status)

    def test_delete_for_author(self):
        note_count_before_delete = Note.objects.count()
        url = self.delete_url
        self.author_client.post(url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, note_count_before_delete - 1)

    def test_delete_for_not_author(self):
        note_before_delete = self.note
        note_count_before_delete = Note.objects.count()
        url = self.delete_url
        self.reader_client.post(url)
        note_counte_after_delete = Note.objects.count()
        self.assertEqual(note_count_before_delete, note_counte_after_delete)
        note_after_delete = Note.objects.get()
        self.assertEqual(note_before_delete.title, note_after_delete.title)
        self.assertEqual(note_before_delete.text, note_after_delete.text)
        self.assertEqual(note_before_delete.slug, note_after_delete.slug)
