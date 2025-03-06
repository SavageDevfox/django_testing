from django.contrib.auth import get_user_model

from .service import BaseTestClass
from notes.forms import NoteForm


User = get_user_model()


class TestContent(BaseTestClass):
    pass

    def test_note_in_list_for_author(self):
        self.client.force_login(self.author)
        url = self.list_url
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_anonymous_user(self):
        self.client.force_login(self.reader)
        url = self.list_url
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_form_on_add_and_edit_pages(self):
        self.client.force_login(self.author)
        for name in (
            self.edit_url,
            self.add_url
        ):
            with self.subTest(name=name):
                url = name
                response = self.client.get(url)
                object_list = response.context
                self.assertIn('form', object_list)
                self.assertIsInstance(response.context['form'], NoteForm)
