from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from suydtdjereo.middleware import SecurityHeadersMiddleware


class SecurityHeadersMiddlewareTests(SimpleTestCase):
    def test_middleware(self):
        def test_view(request):
            return HttpResponse()

        middleware = SecurityHeadersMiddleware(test_view)
        request = RequestFactory().get("/")

        response = middleware(request)

        assert response["Cross-Origin-Embedder-Policy"] == "require-corp"
        assert response["Cross-Origin-Resource-Policy"] == "same-origin"
