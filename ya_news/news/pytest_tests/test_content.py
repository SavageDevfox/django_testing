import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_paginate_home_page(client, create_news_in_bulk, home_url):
    url = home_url
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_sorting_news(client, create_news_in_bulk, home_url):
    url = home_url
    response = client.get(url)
    object_list = response.context['object_list']
    list_of_dates = [news.date for news in object_list]
    sorted_list = sorted(list_of_dates, reverse=True)
    assert sorted_list == list_of_dates


def test_sorting_comments(
        client, news_obj, create_comments_in_bulk, detail_url, comment_obj
):
    url = detail_url
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
    timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(timestamps)
    assert timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_user, form_in_list',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('not_author_client'), True)
    )
)
def test_comment_form_on_page(
        parametrized_user, news_obj, form_in_list, detail_url
):
    url = detail_url
    response = parametrized_user.get(url)
    assert ('form' in response.context) is form_in_list
