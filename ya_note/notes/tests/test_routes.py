from http import HTTPStatus

from django.urls import reverse

from .service import BaseTestClass


class TestRoutes(BaseTestClass):

    def test_home_page(self):
        urls = (
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
            ('notes:home')
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_availability(self):
        self.client.force_login(self.author)
        urls = (
            self.list_url,
            self.add_url,
            self.success_url
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_accessability_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (self.detail_url, self.edit_url, self.delete_url):
                with self.subTest(name=name, user=user):
                    url = name
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.detail_url,
            self.edit_url
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                expected_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
