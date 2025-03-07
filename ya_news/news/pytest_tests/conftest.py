from datetime import timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News
from django.conf import settings


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news_obj():
    return News.objects.create(
        title='Заголовок',
        text='Текст',
    )


@pytest.fixture
def comment_obj(author, news_obj):
    return Comment.objects.create(
        news=news_obj,
        author=author,
        text='Текст'
    )


@pytest.fixture
def pk_for_args(news_obj):
    return (news_obj.id,)


@pytest.fixture
def create_news_in_bulk(db):
    News.objects.bulk_create(
        [News(
            title=f'Новость {i}',
            text=f'Текст {i}',
            date=timezone.now() - timedelta(days=i)
        ) for i in range(
            1, settings.NEWS_COUNT_ON_HOME_PAGE + 2
        )]
    )


@pytest.fixture
def create_comments_in_bulk(news_obj, author, db):
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news_obj,
            author=author,
            text=f'Текст {i}'
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()


@pytest.fixture
def form_data(news_obj, author):
    return {
        'text': 'Текст'
    }


@pytest.fixture
def form_data_edit(news_obj, author):
    return {
        'New': news_obj,
        'author': author,
        'text': 'Исправленный текст'
    }


@pytest.fixture
def string_with_bad_word():
    return f'Какой-то текст и {BAD_WORDS[0]}'


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news_obj):
    return reverse('news:detail', args=(news_obj.id,))


@pytest.fixture
def edit_url(comment_obj):
    return reverse('news:edit', args=(comment_obj.id,))


@pytest.fixture
def delete_url(comment_obj):
    return reverse('news:delete', args=(comment_obj.id,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
