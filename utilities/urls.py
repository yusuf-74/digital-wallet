from django.urls import path

from .views import (
    CurrencyListCreateView,
    CurrencyRetrieveUpdateDestroyView,
    HealthCheck,
    SystemMessagesView,
)

urlpatterns = [
    path('system-messages/', SystemMessagesView.as_view(), name='system-messages'),
    path('health-check/', HealthCheck.as_view(), name='health-check'),
    path('currencies/', CurrencyListCreateView.as_view(), name='currency-list-create'),
    path('currencies/<int:pk>/', CurrencyRetrieveUpdateDestroyView.as_view(), name='currency-retrieve-update-destroy'),
]
