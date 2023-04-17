from http import HTTPStatus

from django.test import TestCase
# from pytest_django.asserts import assertTemplateUsed
# from django.shortcuts import render


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        # Проверьте, что статус ответа сервера - 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
        # return render(request, 'core/404.html', {'path': request.path}, status=404)

    '''
    def test_error_csrf(self):
        response = self.client.get('/403csrf.html')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, 'core/403csrf.html')
        # return render(request, 'core/403csrf.html',
        #               {'path': request.path}, status=403)
    '''
