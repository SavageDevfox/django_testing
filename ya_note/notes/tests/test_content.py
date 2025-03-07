from django.contrib.auth import get_user_model

from .service import BaseTestClass
from notes.forms import NoteForm


User = get_user_model()


class TestContent(BaseTestClass):

    def test_note_in_list_for_author(self):
        for user, assertion in (
            (self.author_client, self.assertIn),
            (self.reader_client, self.assertNotIn)
        ):
            with self.subTest():
                url = self.list_url
                response = user.get(url)
                object_list = response.context['object_list']
                assertion(self.note, object_list)

    def test_form_on_add_and_edit_pages(self):
        for name in (
            self.edit_url,
            self.add_url
        ):
            with self.subTest(name=name):
                url = name
                response = self.author_client.get(url)
                object_list = response.context
                self.assertIn('form', object_list)
                self.assertIsInstance(response.context['form'], NoteForm)
