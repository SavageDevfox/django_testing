import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.parametrize(
    'parametrized_user, comment_is_created',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    )
)
@pytest.mark.django_db
def test_send_comments_for_authorized_user(
    parametrized_user, news_obj, form_data, comment_is_created
):
    url = reverse('news:detail', args=(news_obj.id,))
    parametrized_user.post(url, data=form_data)
    assert Comment.objects.count() == comment_is_created


@pytest.mark.django_db
def test_bad_words(news_obj, author_client, author):
    url = reverse('news:detail', args=(news_obj.id,))
    response = author_client.post(url, data={
        'New': news_obj,
        'author': author,
        'text': f'Какой-то текст и {BAD_WORDS[0]}'})
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_edit_comment_for_author(
    news_obj, comment_obj, author_client, form_data_edit
):
    url = reverse('news:edit', args=(comment_obj.id,))
    response = author_client.post(url, data=form_data_edit)
    assertRedirects(
        response, reverse('news:detail', args=(news_obj.id,)) + '#comments')
    comment_obj.refresh_from_db()
    assert comment_obj.text == form_data_edit['text']


@pytest.mark.django_db
def test_delete_comment_for_author(comment_obj, author_client, news_obj):
    url = reverse('news:delete', args=(comment_obj.id,))
    response = author_client.post(url)
    assertRedirects(
        response, reverse('news:detail', args=(news_obj.id,)) + '#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_edit_for_not_author(not_author_client, comment_obj, form_data_edit):
    url = reverse('news:edit', args=(comment_obj.id,))
    response = not_author_client.post(url, data=form_data_edit)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_to_edit = Comment.objects.get(id=comment_obj.id)
    assert comment_to_edit.text == comment_obj.text


@pytest.mark.django_db
def test_delete_for_not_author(not_author_client, comment_obj):
    url = reverse('news:delete', args=(comment_obj.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
