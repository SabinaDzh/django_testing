from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    """
    Тест проверяет, возможно-ли анононимному пользователю
    создавать комментарии
    """
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, detail_url, form_data, news, author
):
    """
    Тест проверяет, возможно-ли авторизованному
    пользователю создавать комментарии
    """
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url, comment):
    """Тест проверяет "плохие" слова в тексте комментария"""
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response,
                    form='form',
                    field='text',
                    errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_delete_comment(
    delete_url, author_client, url_to_comments
):
    """Тест проверяет возможность удаления комментария автором"""
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    admin_client, delete_url
):
    """
    Тест проверяет, что другой пользователь
    не может удалить комментарии автора
    """
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, edit_url, form_data, comment, url_to_comments
):
    """
    Тест проверяет, что автор может
    изменять (редактировать) свой комментарий
    """
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    admin_client, edit_url, form_data, comment, author, news
):
    """
    Тест проверяет, что другой пользователь
    не может изменять (редактировать) комментарий автора
    """
    comment_text = comment.text
    news = comment.news
    author = comment.author
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author
