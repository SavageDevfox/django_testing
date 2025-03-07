from http import HTTPStatus

import pytest
from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        pytest.lazy_fixture('home_url'),
        pytest.lazy_fixture('login_url'),
        pytest.lazy_fixture('logout_url'),
        pytest.lazy_fixture('signup_url'),
        pytest.lazy_fixture('detail_url')
    )
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name):
    url = name
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ))
@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'))
)
def test_comment_edit_and_delete_availability_for_users(
    parametrized_client, expected_status, name
):
    url = name
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('edit_url'), pytest.lazy_fixture('delete_url'))
)
def test_redirect_for_anonymous_user(client, name):
    login_url = reverse('users:login')
    url = name
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
