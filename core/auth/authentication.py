import os

# FOR SWAGGER
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication

from authentication.models import User


class XAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if request.META.get('HTTP_X_API_KEY') and request.META.get('HTTP_X_API_KEY') == os.environ.get('X_API_KEY'):
            return (User.objects.get(id=1), None)
        return None

    def authenticate_header(self, request):
        return 'X-API-KEY'


class XAPIKeyAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = 'core.auth.authentication.XAPIKeyAuthentication'
    name = 'X-API-KEY'
    priority = 1

    # OpenAPI 2.0
    def get_security_definition(self, auto_schema):
        return {'type': 'apiKey', 'in': 'header', 'name': 'X-API-KEY'}

    # OpenAPI 3.0
    def get_security_requirement(self, auto_schema):
        return [{'X-API-KEY': []}]
