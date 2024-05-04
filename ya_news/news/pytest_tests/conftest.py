from datetime import datetime, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Александр Пушкин')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def detail_url(news_id, news):
    return reverse('news:detail', args=news_id)


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    form_data = {'text': 'Текст комментария'}
    form_data = {'text': 'Обновлённый комментарий'}
    return form_data


@pytest.fixture
def url_to_comments(detail_url):
    url_to_comments = detail_url + '#comments'
    return url_to_comments


@pytest.fixture
def edit_url(comment_id):
    return reverse('news:edit', args=comment_id)


@pytest.fixture
def delete_url(comment_id):
    return reverse('news:delete', args=comment_id)
