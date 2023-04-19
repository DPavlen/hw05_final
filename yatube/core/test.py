from http import HTTPStatus

# from django.shortcuts import render
from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/page_not_found/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
        # return render(response, 'core/404.html')

    '''
    def test_error_csrf(self):
        response = self.client.get('/403csrf.html')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, 'core/403csrf.html')
        # return render(request, 'core/403csrf.html',
        #               {'path': request.path}, status=403)
    '''
