from datetime import datetime

from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.base.views import (
    UnifiedResponseListCreateAPIView,
    UnifiedResponseRetrieveUpdateDestroyAPIView,
)
from utils.orm_utils import query_optimizer

from .filters import CurrencyFilter
from .models import Currency, SystemMessage
from .serializers import CurrencySerializer, SystemMessagesSerializer


@extend_schema(
    tags=['System Messages'],
    description="This API will return the latest system message that is active and released to the user based on the user's group. If the user is an admin, then the message will be returned regardless of the user's group.",
    responses={200: SystemMessagesSerializer, 204: None},
)
class SystemMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_204_NO_CONTENT)

        users_groups = list(request.user.groups.values_list('id', flat=True))
        admin_group = Group.objects.filter(name__icontains='Admins').values('id').first()
        is_admin = admin_group['id'] in users_groups or request.user.is_superuser

        query_criteria = Q(release_date__lte=timezone.now()) & Q(end_at__gte=timezone.now()) & Q(status=True)
        if not is_admin:
            query_criteria = query_criteria & (Q(groups__in=users_groups) | Q(is_restricted=False))

        message = (
            SystemMessage.objects.prefetch_related('groups').filter(query_criteria).order_by('-release_date').first()
        )
        if not message:
            return Response(status=status.HTTP_204_NO_CONTENT)
        message_serializer = SystemMessagesSerializer(message)
        return Response(message_serializer.data, status=status.HTTP_200_OK)


class CurrencyListCreateView(UnifiedResponseListCreateAPIView):
    serializer_class = CurrencySerializer
    filterset_class = CurrencyFilter

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return query_optimizer(Currency, self.request)


@extend_schema(
    tags=['Wallets'],
    responses={200: CurrencySerializer, 204: None},
)
class CurrencyRetrieveUpdateDestroyView(UnifiedResponseRetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CurrencySerializer

    def get_queryset(self):
        return query_optimizer(Currency, self.request)


class HealthCheck(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - OK", status=status.HTTP_200_OK)
