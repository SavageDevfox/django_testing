import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_send_comments_for_authorized_user(
        author_client, news_obj, form_data, detail_url
):
    url = detail_url
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']


def test_send_comments_for_anonymous_user(
        client, news_obj, form_data, detail_url
):
    url = detail_url
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_bad_words(
        news_obj, author_client, author, string_with_bad_word, detail_url
):
    url = detail_url
    response = author_client.post(url, data={
        'text': string_with_bad_word})
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_edit_comment_for_author(
        news_obj, comment_obj, author_client, form_data_edit, edit_url,
        detail_url
):
    url = edit_url
    response = author_client.post(url, data=form_data_edit)
    assertRedirects(
        response, detail_url + '#comments')
    comment_obj.refresh_from_db()
    assert comment_obj.text == form_data_edit['text']


def test_delete_comment_for_author(
        comment_obj, author_client, news_obj, delete_url, detail_url
):
    url = delete_url
    response = author_client.post(url)
    assertRedirects(
        response, detail_url + '#comments')
    assert Comment.objects.count() == 0


def test_edit_for_not_author(
        not_author_client, comment_obj, form_data_edit, edit_url
):
    url = edit_url
    response = not_author_client.post(url, data=form_data_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_to_edit = Comment.objects.get(id=comment_obj.id)
    assert comment_to_edit.text == comment_obj.text


def test_delete_for_not_author(not_author_client, comment_obj, delete_url):
    url = delete_url
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
