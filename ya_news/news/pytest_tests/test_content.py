import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(all_news, client):
    """Тест проверяет количество новостей на главной странице"""
    response = client.get(reverse('news:home'))
    object_list = response.context.get('object_list', [])
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Тест проверяет сортировку новостей по дате"""
    response = client.get(reverse('news:home'))
    object_list = response.context.get('object_list', [])
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, detail_url):
    """Тест проверяет сортировку комментариев от нового к старому"""
    response = client.get(detail_url)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    sorte_comments = (all_comments)
    assert all_comments == sorte_comments


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Тест проверяет отсутствие формы у анонимного пользователя"""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url):
    """Тест проверяет наличие формы для авторизованного пользователя"""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    form = response.context['form']
    assert isinstance(form, CommentForm)
