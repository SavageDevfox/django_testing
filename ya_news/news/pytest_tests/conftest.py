import pytest

from datetime import timedelta

from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


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
    news_obj = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news_obj


@pytest.fixture
def comment_obj(author, news_obj):
    comment_obj = Comment.objects.create(
        news=news_obj,
        author=author,
        text='Текст'
    )
    return comment_obj


@pytest.fixture
def pk_for_args(news_obj):
    return (news_obj.id,)


@pytest.fixture
def create_news_in_bulk(db):
    return News.objects.bulk_create(
        [News(
            title=f'Новость {i}',
            text=f'Текст {i}',
            date=timezone.now() - timedelta(days=i)
        ) for i in range(
            1, NEWS_COUNT_ON_HOME_PAGE + 2
        )]
    )


@pytest.fixture
def create_comments_in_bulk(news_obj, author, db):
    comments = []
    for i in range(NEWS_COUNT_ON_HOME_PAGE):
        comment = Comment.objects.create(
            news=news_obj,
            author=author,
            text=f'Текст {i}'
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()
        comments.append(comment)
    return comments


@pytest.fixture
def form_data(news_obj, author):
    return {
        'New': news_obj,
        'author': author,
        'text': 'Текст'
    }


@pytest.fixture
def form_data_edit(news_obj, author):
    return {
        'New': news_obj,
        'author': author,
        'text': 'Исправленный текст'
    }
