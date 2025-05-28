from django.shortcuts import redirect
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import IsAuthenticated


class AuthenticatedSwaggerView(SpectacularSwaggerView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/api/api-auth/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedSchemaView(SpectacularAPIView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/api/api-auth/login/?next={request.path}')
        return super().dispatch(request, *args, **kwargs)
